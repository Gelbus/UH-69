import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtCore import pyqtSlot   # Именно так!


class VideoThread(QThread):
    """Поток для захвата видео из OpenCV"""
    change_pixmap_signal = pyqtSignal(np.ndarray)  # Передаём numpy-массив (кадр)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # cap = cv2.VideoCapture(0)  # 0 — веб-камера, или путь к видео-файлу
        url = 'http://192.168.1.23:5000/'

        cap = cv2.VideoCapture(url)
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                self.change_pixmap_signal.emit(frame)
        cap.release()

    def stop(self):
        """Останавливаем поток"""
        self._run_flag = False
        self.wait()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCV → Qt (PyQt5)")
        self.setGeometry(100, 100, 800, 600)

        # QLabel для отображения видео
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Запускаем поток
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def closeEvent(self, event):
        """Корректно останавливаем поток при закрытии окна"""
        self.thread.stop()
        event.accept()

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
        scaled_pixmap = pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())