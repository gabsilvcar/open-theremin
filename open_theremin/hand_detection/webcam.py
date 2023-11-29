import sys
import cv2
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QStatusBar

class Webcam(QLabel):
    def __init__(self, detector, cap, parent=None):
        self.cap = cap
        super().__init__(parent)
        self.detector = detector
        # Timer to update the webcam feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)  # Adjust frame rate as needed

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            detections = self.detector.detect_async(frame)
            frame = self.detector.draw(frame, detections)

            q_img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.setPixmap(pixmap)

    def close(self):
        self.timer.stop()
        self.detector.close()
        super().close()
