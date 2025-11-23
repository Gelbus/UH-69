import cv2
import socket
from flask import Flask, Response, request, jsonify
from typing import Optional, Dict, Any


class RobotVideoServer:
    def __init__(
        self,
        platform,
        host: str = "0.0.0.0",
        port: int = 5000,
        camera_id: int = 0,
        width: int = 640,
        height: int = 360,
        fps: int = 30,
        jpeg_quality: int = 60
    ):
        self.platform = platform
        self.host = host
        self.port = port
        self.jpeg_quality = jpeg_quality

        self.app = Flask(__name__)
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps

        self.latest_command = "ожидание..."
        self.last_data_from_client: Dict[str, Any] = {}

        self._setup_camera()
        self._setup_routes()

    def _setup_camera(self) -> None:
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Прогрев камеры (чтобы первый кадр не висел)
        print("Прогрев камеры...")
        for _ in range(15):
            ret, _ = self.cap.read()
            if ret:
                break
        print("Камера готова")

    def _setup_routes(self) -> None:
        """Регистрация всех маршрутов"""

        @self.app.route('/')
        def index():
            return Response(self._generate_frames(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/send', methods=['POST'])
        def receive_from_client():
            data = request.get_json(silent=True) or {}
            self.latest_command = data.get('command', 'без команды')
            self.last_data_from_client = data
            print(f"Команда от клиента: {data}")
            self.platform.setup(data['path'], data['yaw'])
            return jsonify({"status": "ok", "received": data}), 200

        @self.app.route('/get')
        def send_to_client():
            # Здесь можно добавить try/except, если platform временно недоступен
            sensor_data = {
                "x": getattr(self.platform, 'x', 0),
                "y": getattr(self.platform, 'y', 0),
                "yaw": getattr(self.platform, 'yaw', 0),
                "command": self.latest_command
            }
            return jsonify(sensor_data)

        # Дополнительно: можно добавить маршрут для текущей команды
        @self.app.route('/status')
        def status():
            return jsonify({
                "latest_command": self.latest_command,
                "last_client_data": self.last_data_from_client,
                "camera_opened": self.cap.isOpened() if self.cap else False
            })

    def _generate_frames(self):
        """Генератор кадров для MJPEG-потока"""
        while True:
            if not self.cap or not self.cap.isOpened():
                # Если камера отвалилась — пытаемся переподключить
                self._setup_camera()

            ret, frame = self.cap.read()
            if not ret:
                continue

            ret, buffer = cv2.imencode(
                '.jpg', frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
            )
            if not ret:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def run(self, debug=False, use_reloader=False):
        """
        Запуск сервера.
        При запуске на малине debug=False, use_reloader=False.
        """
        print(f"Сервер запускается на http://{socket.gethostbyname(socket.gethostname())}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug,
            use_reloader=use_reloader,
            threaded=True
        )

    def stop(self):
        """Освобождение ресурсов"""
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Видеосервер остановлен")
