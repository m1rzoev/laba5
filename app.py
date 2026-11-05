from flask import Flask, jsonify, request

app = Flask(__name__)

# база данных (список задач в памяти)
tasks = [
    {"id": 1, "title": "Изучить Nginx"},
    {"id": 2, "title": "Сделать лабу"}
]

# 1. GET /api/health - состояние сервера
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Сервер работает стабильно"}), 200

# 2. GET /api/tasks - получить список задач
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks), 200

# 3. POST /api/tasks - добавить задачу
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Не передано название задачи"}), 400
    
    new_task = {
        "id": len(tasks) + 1,
        "title": data['title']
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

if __name__ == '__main__':
    
    app.run(host='127.0.0.1', port=5000) #запуск
