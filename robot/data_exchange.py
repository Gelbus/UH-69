# server.py
import random

from flask import Flask, Response, request, jsonify
import threading
import time
import cv2


app = Flask(__name__)

# Здесь будут храниться последние данные от клиента (например, команды)
latest_command = "ожидание..."
last_data_from_client = {}

# Открываем камеру через OpenCV
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

platform = None


def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Кодируем в JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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
    # return jsonify({"status": "error", "message": "Нет данных"}), 400


# Клиент запрашивает данные ОТ СЕРВЕРА (например, температура, статус реле и т.д.)
@app.route('/get')
def send_to_client():
    # Здесь ты можешь собрать любые данные с платы
    sensor_data = {
        "x": platform.x,
        "y": platform.y,
        "yaw": platform.yaw
    }
    return jsonify(sensor_data)


def run_exchange(myplatform):
    global platform
    platform = myplatform
    app.run(host='0.0.0.0', port=5000, debug=True)