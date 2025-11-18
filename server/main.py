import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                             QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMouseEvent

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtCore import pyqtSlot   # Именно так!
import time

class MapWidget(QLabel):
    # Собственный виджет карты

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True) # Отслеживать мышь
        self.setStyleSheet(
            """
                background-color: lightgray;
                border: 1px solid black;
            """
        )
        self.setFixedSize(512, 384)
        self.last_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            print(f"Map clicked at: {event.pos()}")
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        # Basic drawing functionality
        if event.buttons() & Qt.LeftButton and self.last_pos:
            print(f"Drawing from {self.last_pos} to {event.pos()}")
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.last_pos = None


class VideoThread(QThread):
    """Поток для захвата видео из OpenCV"""
    change_pixmap_signal = pyqtSignal(np.ndarray)  # Передаём numpy-массив (кадр)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.url = 'http://192.168.1.23:5000/'


    def run(self):
        cap = cv2.VideoCapture(self.url)

        while self._run_flag:
            ret, frame = cap.read()

            if ret:
                self.change_pixmap_signal.emit(frame)
            else:
                print("Кадр не получен, переподключаемся...")
                cap.release()
                cap = cv2.VideoCapture(self.url)
                time.sleep(1)  # небольшая пауза перед повторным подключением
                continue
        cap.release()

    def stop(self):
        """Останавливаем поток"""
        self._run_flag = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализируем окно
        self.setWindowTitle("UH-69 Control Interface")
        self.setGeometry(500, 500, 1400, 800)
        self.setFixedSize(self.size())


        # Создаём главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)


        # Левый столбец
        left_layout = QVBoxLayout()

        # Создаем список параметров
        self.param_list = QListWidget()
        self.param_list.setFixedSize(300, 300)
        self.param_list.addItems(
            [
            "Param1: 0.0",
            "Param2: 0.0",
            "Param3: 0.0"
            ]
        )
        left_layout.addWidget(self.param_list)


        # Создаём кнопки
        self.button_area = QWidget()
        button_layout = QVBoxLayout(self.button_area)
        button_layout.setAlignment(Qt.AlignBottom)

        self.button1 = QPushButton("Button 1")
        self.button1.setFixedSize(300, 50)

        self.button2 = QPushButton("Button 2")
        self.button2.setFixedSize(300, 50)

        self.button3 = QPushButton("Button 3")
        self.button3.setFixedSize(300, 50)

        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)

        left_layout.addWidget(self.button_area)


        # Правый столбец, карта и камеры
        right_layout = QVBoxLayout()


        # Добавляю камеры
        camera_top_layout = QHBoxLayout()
        self.camera1_label = QLabel("No signal")
        self.camera1_label.setStyleSheet("""
            background-color: black;
            color: red;
            qproperty-alignment: AlignCenter;
            """)
        self.camera1_label.setFixedSize(512, 384)
        camera_top_layout.addWidget(self.camera1_label)

        right_layout.addLayout(camera_top_layout)


        # Карта
        self.map_widget = MapWidget()
        right_layout.addWidget(self.map_widget)


        # Добавляю левый и правый столбцы на главный виджет
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addLayout(right_layout, 0, 1)

        # Запускаем поток
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        # Так я могу прятать кнопки
        # self.button2.hide()

    def toggle_buttons(self):
        """Example function to show/hide buttons."""
        # This is a placeholder for your logic to show/hide buttons
        # For example, you could toggle visibility based on state
        pass

    def update_parameters(self):
        """Placeholder for updating parameters at 10Hz."""
        # This function would be called by a QTimer in a real implementation
        pass

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Преобразуем кадр OpenCV в QPixmap и отображаем"""
        # BGR → RGB
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # Масштабируем под размер QLabel (с сохранением пропорций)
        # scaled_pixmap = pixmap.scaled(self.camera1_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera1_label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())