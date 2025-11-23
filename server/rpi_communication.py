# rpi_communication.py
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import requests
import time
import json
import cv2
import numpy as np


class VideoThread(QThread):
    """Поток для захвата видео из OpenCV"""
    change_pixmap_signal = pyqtSignal(np.ndarray)  # Передаём numpy-массив (кадр)

    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__()
        self._run_flag = True
        self.server_url = server_url


    def run(self):
        cap = cv2.VideoCapture(self.server_url)

        while self._run_flag:
            ret, frame = cap.read()

            if ret:
                self.change_pixmap_signal.emit(frame)
            else:
                print("Кадр не получен, переподключаемся...")
                cap.release()
                cap = cv2.VideoCapture(self.server_url)
                time.sleep(1)  # небольшая пауза перед повторным подключением
                continue
        cap.release()

    def stop(self):
        """Останавливаем поток"""
        self._run_flag = False
        self.wait()


class RpiSignals(QObject):
    telemetry_received = pyqtSignal(dict)   # новые данные с Pi
    command_sent = pyqtSignal(str)          # команда ушла
    error = pyqtSignal(str)                 # ошибка сети
    connected = pyqtSignal()                # первое подключение
    disconnected = pyqtSignal()


class RpiCommunicationThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)  # Передаём numpy-массив (кадр)

    def __init__(self, server_url="http://127.0.0.1:5000", interval=1.0):
        super().__init__()
        self.server_url = server_url
        self.interval = interval
        self.running = True
        self.pending_command = None
        self.pending_path = None  # для отправки маршрута
        self.pending_yaw = None
        self.signals = RpiSignals()


    def run(self):
        was_connected = False
        while self.running:
            try:
                # 1. Отправляем команду или путь, если есть
                if self.pending_command:
                    self._send_command(self.pending_command)
                    self.pending_command = None
                if self.pending_path and (not self.pending_yaw is None):
                    self._send_init(self.pending_path, self.pending_yaw)
                    self.pending_path = None

                # 2. Запрашиваем телеметрию
                data = self._get_telemetry()
                if data:
                    self.signals.telemetry_received.emit(data)
                    if not was_connected:
                        was_connected = True
                        self.signals.connected.emit()

            except requests.exceptions.RequestException as e:
                if was_connected:
                    was_connected = False
                    self.signals.disconnected.emit()
                self.signals.error.emit("Робот не шлёт данных")
            except Exception as e:
                self.signals.error.emit(f"Ошибка: {e}")

            time.sleep(self.interval)

    def _send_command(self, cmd):
        payload = {"command": cmd, "from": "qt_control"}
        r = requests.post(f"{self.server_url}/send", json=payload, timeout=3)
        if r.status_code == 200:
            self.signals.command_sent.emit(cmd)

    def _send_init(self, path_list, yaw):
        payload = {
            "command": "path",
            "path": path_list,  # [[x1,y1], [x2,y2], ...]
            "yaw": yaw,
            "from": "server"
        }
        print(payload)
        r = requests.post(f"{self.server_url}/send", json=payload, timeout=10)
        if r.status_code == 200:
            self.signals.command_sent.emit("autonomous_path")

    def _get_telemetry(self):
        r = requests.get(f"{self.server_url}/get", timeout=3)
        if r.status_code == 200:
            return r.json()
        return None

    # Вызываются из главного потока
    def send_simple_command(self, cmd):
        self.pending_command = cmd

    def send_init(self, path_points, yaw):
        self.pending_path = path_points#[[float(x), float(y)] for x, y in path_points]
        self.pending_yaw = yaw

    def stop(self):
        self.running = False
        self.wait()