import sys

from PyQt6.QtWidgets import QApplication

from hand_detection import Detector, Webcam
from hand_detection_classic import DetectorClassic, WebcamClassic

app = QApplication(sys.argv)
detector = Detector()
webcam = Webcam(detector)
sys.exit(app.exec())
# detector = DetectorClassic()
# webcam = WebcamClassic(detector)
