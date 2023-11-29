import cv2
import mediapipe as mp
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel
from mediapipe import ImageFormat

class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        # Add a label and set a pixmap
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap('path_to_your_image.jpg'))  # Replace with your image path
        # Resize the label to fit the image
        self.label.resize(self.label.pixmap().size())

        # Show the window
        self.show()

class Webcam(QWidget):
    def __init__(self, detector):
        super().__init__()

        # Set window properties
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        self.label = QLabel(self)

        # access webcam
        cap = cv2.VideoCapture(0)

        while True:
            # pull frame
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            # mirror frame
            # frame = cv2.flip(frame, 1)
            # update landmarker results
            detector.detect_async(frame)

            frame = detector.draw(frame)

            self.label = QLabel(self)
            self.label.setPixmap(frame)  # Replace with your image path

            # display image
            # cv2.imshow("frame", frame)
            self.show()

            if cv2.waitKey(1) == ord("q"):
                break

        # release everything
        detector.close()
        cap.release()
        cv2.destroyAllWindows()
