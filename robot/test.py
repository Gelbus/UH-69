# server.py
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Здесь будут храниться последние данные от клиента (например, команды)
latest_command = "ожидание..."
last_data_from_client = {}


# Клиент отправляет данные СЕРВЕРУ (например, команда "включи свет")
@app.route('/send', methods=['POST'])
def receive_from_client():
    global latest_command, last_data_from_client

    data = request.get_json()
    if data:
        latest_command = data.get('command', 'без команды')
        last_data_from_client = data
        print(f"Получено от клиента: {data}")
        return jsonify({"status": "ok", "received": data}), 200
    return jsonify({"status": "error", "message": "Нет данных"}), 400


# Клиент запрашивает данные ОТ СЕРВЕРА (например, температура, статус реле и т.д.)
@app.route('/get')
def send_to_client():
    # Здесь ты можешь собрать любые данные с платы
    sensor_data = {
        "temperature": 23.5,
        "humidity": 45,
        "led_status": "on",
        "uptime": time.time() - start_time,
        "last_command": latest_command
    }
    return jsonify(sensor_data)


# Запуск сервера
if __name__ == '__main__':
    global start_time
    start_time = time.time()
    print("Запускаю сервер на http://0.0.0.0:5000")
    print("Для теста на одном ПК используй http://127.0.0.1:5000")
    print("Когда перенесёшь на Raspberry Pi — подключись по её IP, например: http://192.168.1.35:5000")

    # Важно: host='0.0.0.0' — чтобы сервер был доступен извне
    app.run(host='0.0.0.0', port=5000, debug=True)