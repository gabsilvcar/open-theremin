from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class PlaceholderWebcam(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set default text, alignment, and style
        self.setText("Webcam Feed Here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black; color: white;")
