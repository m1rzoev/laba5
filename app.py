from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = 'tasks.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Сервер работает стабильно"}), 200

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
    conn.close()
    
    tasks_list = [dict(task) for task in tasks]
    for task in tasks_list:
        task['completed'] = bool(task['completed'])
    return jsonify(tasks_list), 200

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Название задачи обязательно"}), 400
        
    title = data['title'].strip()
    if not (1 <= len(title) <= 200):
        return jsonify({"error": "Название должно быть от 1 до 200 символов"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, completed) VALUES (?, ?)', (title, False))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "title": title, "completed": False}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.get_json()
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if not task:
        conn.close()
        return jsonify({"error": "Задача не найдена"}), 404

    if 'title' in data:
        title = data['title'].strip()
        if not (1 <= len(title) <= 200):
            conn.close()
            return jsonify({"error": "Название должно быть от 1 до 200 символов"}), 400
    
    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            conn.close()
            return jsonify({"error": "completed должно быть логическим значением (true/false)"}), 400

    new_title = data.get('title', task['title']).strip()
    new_completed = data.get('completed', bool(task['completed']))

    conn.execute('UPDATE tasks SET title = ?, completed = ? WHERE id = ?', 
                 (new_title, new_completed, task_id))
    conn.commit()
    conn.close()

    return jsonify({"id": task_id, "title": new_title, "completed": new_completed}), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if not task:
        conn.close()
        return jsonify({"error": "Задача не найдена"}), 404

    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Задача успешно удалена"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000)
