import sys

import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox

from open_theremin.hand_detection import Webcam, Detector
from open_theremin.hand_detection_classic import DetectorClassic, WebcamClassic
from open_theremin.interface.placeholder_webcam import PlaceholderWebcam


class MainWindow(QMainWindow):
    CLASSIC_VISION = "Classic Computer Vision"
    CONVOLUTIONAL_VISION = "Convolutional Computer Vision"
    NO_SOURCE = "No source"
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

        # Set up the main window
        self.setWindowTitle('Open Theremin')
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.main_layout = QVBoxLayout()

        self.webcam_source = PlaceholderWebcam()
        self.main_layout.addWidget(self.webcam_source)

        # Source selection area
        source_selection_layout = QHBoxLayout()
        self.source_selector = QComboBox()
        self.source_selector.addItems([self.NO_SOURCE, self.CLASSIC_VISION, self.CONVOLUTIONAL_VISION])
        source_selection_layout.addWidget(self.source_selector)

        # Button to apply source selection
        apply_button = QPushButton("Apply Source")
        apply_button.clicked.connect(self.apply_source_selection)
        source_selection_layout.addWidget(apply_button)

        self.main_layout.addLayout(source_selection_layout)

        # Frequency display
        self.frequency_display = QLabel("Frequency: -- Hz")
        self.main_layout.addWidget(self.frequency_display)

        # Set the main layout
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def apply_source_selection(self):
        selected_source = self.source_selector.currentText()
        # Placeholder for actual source switching logic
        if selected_source == self.CLASSIC_VISION:
            new_source = Webcam(DetectorClassic(), self.cap)
        if selected_source == self.CONVOLUTIONAL_VISION:
            new_source = Webcam(Detector(), self.cap)
        if selected_source == self.NO_SOURCE:
            new_source = PlaceholderWebcam()
        print(f"Selected Source: {selected_source}")
        # Replace the old webcam widget with the new one
        self.main_layout.replaceWidget(self.webcam_source, new_source)
        self.webcam_source.close()  # Close the old widget
        self.webcam_source = new_source  # Update the reference

    def update_frequency_display(self, new_frequency):
        self.frequency_display.setText(f"Frequency: {new_frequency}")

    def close(self):
        self.cap.release()

