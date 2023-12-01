import argparse

import cv2


class DetectorClassic:
    def __init__(self):
        # Loads a cascade classifier model
        self.cascade = cv2.CascadeClassifier()
        self.cascade.load(
            "model/aGest.xml"
        )  # Haar model for detection of fists developed by https://github.com/Aravindlivewire/Opencv/blob/master/haarcascade/aGest.xml

    def detect_async(self, frame):
        # Image preparation
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        # Detection of hands
        detections = self.cascade.detectMultiScale(frame_gray)

        return detections

    def draw(self, frame, detections):
        # Draw on the frame the two detected objects most likely to be hands
        for x, y, w, h in detections[0:2:1]:
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 4)

        return frame

    def hand_pos(self, detections):
        for x, y, w, h in detections[0:2:1]:
            return x + w / 2, y + h / 2
        return 0, 0

    def close(self):
        pass
