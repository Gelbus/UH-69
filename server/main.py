import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                             QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMouseEvent


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
        self.setFixedSize(1024, 300)  # Set a minimum size
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


        self.camera2_label = QLabel("No signal")
        self.camera2_label.setStyleSheet("""
            background-color: black;
            color: red;
            qproperty-alignment: AlignCenter;
            """)
        self.camera2_label.setFixedSize(512, 384)
        camera_top_layout.addWidget(self.camera2_label)

        right_layout.addLayout(camera_top_layout)


        # Карта
        self.map_widget = MapWidget()
        right_layout.addWidget(self.map_widget)


        # Добавляю левый и правый столбцы на главный виджет
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addLayout(right_layout, 0, 1)

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

    def update_camera_feeds(self):
        """Placeholder for updating camera image feeds."""
        # This function would receive image data and update the QLabel pixmaps
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())