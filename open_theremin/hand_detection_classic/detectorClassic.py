import argparse

import cv2
import numpy as np


class DetectorClassic:
    def __init__(self):
        # Loads a cascade classifier model
        self.cascade = cv2.CascadeClassifier()
        self.cascade.load(
            "model/cascade.xml"
        )  # Haar model for detection of fists developed by https://github.com/Aravindlivewire/Opencv/blob/master/haarcascade/aGest.xml

    def detect_async(self, frame):
        # Image preparation
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        # Detection of hands
        detections = self.cascade.detectMultiScale(frame_gray)

        # Normalizing detections
        width = frame_gray.shape[0]
        height = frame_gray.shape[1]
        detections_norm: list = []
        for x, y, w, h in detections:
            detections_norm.append(
                np.array(
                    [
                        (x / (float)(width)),
                        (y / (float)(height)),
                        (w / (float)(width)),
                        (h / (float)(height)),
                    ]
                )
            )

        return detections_norm

    def draw(self, frame, detections):
        # Draw on the frame the two detected objects most likely to be hands
        width = frame.shape[0]
        height = frame.shape[1]
        for x, y, w, h in detections[0:2:1]:
            frame = cv2.rectangle(
                frame,
                ((int)(x * width), (int)(y * height)),
                ((int)((x + w) * width), (int)((y + h) * height)),
                (255, 0, 255),
                4,
            )

        return frame

    def hand_pos(self, detections):
        for x, y, w, h in detections[0:2:1]:
            return x + w / 2, y + h / 2
        return 0, 0

    def close(self):
        pass
