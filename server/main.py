import sys
from turtledemo.penrose import start

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
from astar import PathGenerator

from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor

import rpi_communication as rc


class MapWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setStyleSheet("""
            background-color: lightgray;
            border: 10px solid green;
            border-radius: 15px;
        """)
        self.setFixedSize(640, 360)
        self.impath = "../data/maps/map1.png"

        # Загружаем карту как фон
        self.base_pixmap = QPixmap(self.impath).scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.setPixmap(self.base_pixmap)

        # Буфер для рисования (чтобы не перерисовывать карту каждый раз)
        self.drawing_pixmap = QPixmap(self.size())
        self.drawing_pixmap.fill(Qt.transparent)

        # Данные для рисования
        self.points = {
            "start": [],
            "target": [],
            "finish": [],
            "robot": [],
        }
        self.qpoints = []

        # Настройки
        self.start_point_color = QColor(200, 200, 200)  # серая точки
        self.target_point_color = QColor(150, 150, 150)  # красные точки
        self.finish_point_color = QColor(100, 100, 100)  # черные точки
        self.robot_point_color = QColor(0, 255, 0)  # зеленые точки

        self.line_color = QColor(0, 0, 255)  # синие линии
        self.point_size = 50
        self.line_width = 3

    # === Рисование точек левой кнопкой ===
    def mousePressEvent(self, event):
        pos = event.pos()

        if event.button() == Qt.LeftButton:
            self.points["start"] = [pos, self.start_point_color]

        elif event.button() == Qt.MiddleButton:
            self.points["target"] = [pos, self.target_point_color]

        elif event.button() == Qt.RightButton:
            self.points["finish"] = [pos, self.finish_point_color]

        self.update_drawing()  # перерисовываем только слой с рисунками

    # === Перерисовка только слоя с рисунками ===
    def update_drawing(self):
        self.drawing_pixmap.fill(Qt.transparent)
        painter = QPainter(self.drawing_pixmap)

        # Рисуем все точки
        for key, value in self.points.items():
            if self.points[key]:
                pos = self.points[key][0]
                color = self.points[key][1]
                painter.setPen(QPen(color, self.point_size, Qt.SolidLine, Qt.RoundCap))
                painter.drawPoint(pos)

        # Рисуем маршрут
        if self.qpoints:
            for path in self.qpoints:
                pen = QPen(self.line_color, self.line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawPolyline(*path)

        painter.end()
        self.update()  # вызывает paintEvent

    # === Основной paintEvent — накладываем карту + рисунки ===
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.base_pixmap)
        painter.drawPixmap(0, 0, self.drawing_pixmap)

    # === Удобные методы для очистки и управления ===
    def clear_all(self):
        self.points.clear()
        self.lines.clear()
        self.drawing_pixmap.fill(Qt.transparent)
        self.update()

    def clear_points(self):
        self.points.clear()
        self.update_drawing()

    def clear_lines(self):
        self.lines.clear()
        self.update_drawing()


    def set_lines(self, paths):
        self.qpoints = [[QPoint(x, y) for x, y in path] for path in paths]
        self.update_drawing()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализируем окно
        self.path_generator = None
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
            "Позиция платформы X: 0.0",
            "Позиция платформы Y: 0.0",
            "Курс платформы: 0.0",

            "Позиция башни X: 0.0",
            "Позиция башни Z: 0.0",
            "Курс башни: 0.0"
            ]
        )
        left_layout.addWidget(self.param_list)


        # Создаём кнопки
        self.button_area = QWidget()
        button_layout = QVBoxLayout(self.button_area)
        button_layout.setAlignment(Qt.AlignBottom)

        self.button1 = QPushButton("Автономное управление")
        self.button1.setFixedSize(300, 50)
        self.button1.clicked.connect(self.auto_btn)

        self.button2 = QPushButton("Ручное управление")
        self.button2.setFixedSize(300, 50)

        self.button3 = QPushButton("Демонстрация")
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
            border: 10px solid red;
            border-radius: 15px;
            """)
        self.camera1_label.setFixedSize(640, 360)
        camera_top_layout.addWidget(self.camera1_label)

        right_layout.addLayout(camera_top_layout)

        # Карта
        self.map_widget = MapWidget()
        right_layout.addWidget(self.map_widget)


        # Добавляю левый и правый столбцы на главный виджет
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addLayout(right_layout, 0, 1)


        self.rpi_url = "http://127.0.0.1:5000"  # ← ТУТ IP твоей малины или 127.0.0.1 для теста

        # Запускаем поток видео
        self.thread = rc.VideoThread(self.rpi_url)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        # Запускаем поток обмена командами и телеметрией
        self.rpi_thread = rc.RpiCommunicationThread(server_url=self.rpi_url, interval=0.5)
        self.rpi_thread.signals.telemetry_received.connect(self.update_telemetry)
        self.rpi_thread.signals.command_sent.connect(lambda cmd: print(f"Отправлено: {cmd}"))
        self.rpi_thread.signals.connected.connect(lambda: print("Подключено к роботу!"))
        self.rpi_thread.start()

    def _to_tuple_pos(self, qtpos):
        pos = (qtpos.x(), qtpos.y())
        print(pos)
        return pos


    def auto_btn(self):

        if not self.map_widget.points["start"] or not self.map_widget.points["target"]:
            print("Не заданы стартовая и целевая точки!")
            return
        
        start_p = self._to_tuple_pos(self.map_widget.points["start"][0])
        target_p = self._to_tuple_pos(self.map_widget.points["target"][0])
        finish_p = self._to_tuple_pos(self.map_widget.points["finish"][0])
        
        self.path_generator = PathGenerator(
            start_p,
            target_p,
            finish_p,
            self.map_widget.impath
        )

        waypoints1, waypoints2 = self.path_generator.get_path()
        data = [waypoints1, waypoints2]
        self.map_widget.set_lines(data)

        # === ОТПРАВЛЯЕМ ПУТЬ НА МАЛИНУ ===
        self.rpi_thread.send_path(data)

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
        # Приём телеметрии

    def update_telemetry(self, data):
        try:
            self.param_list.item(0).setText(f"Позиция платформы X: {data.get('x', 0):.1f}")
            self.param_list.item(1).setText(f"Позиция платформы Y: {data.get('y', 0):.1f}")
            self.param_list.item(2).setText(f"Позиция платформы YAW: {data.get('yaw', 0):.1f}")

        except:
            pass
        # "Позиция платформы Y: 0.0",
        # "Курс платформы: 0.0",
        # self.label_x.setText(f"X: {data['x']}")
        # self.label_y.setText(f"Y: {data['y']}")
        # self.label_z.setText(f"Z: {data['z']}")
        # self.label_angle.setText(f"Угол: {data['angle']}")
        # self.label_battery.setText(f"Аккум: {data['battery']}%")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())