import cv2
import mediapipe as mp
from mediapipe import ImageFormat


class Webcam:
    def __init__(self, detector):
        # access webcam
        cap = cv2.VideoCapture(0)

        while True:
            # pull frame
            ret, frame = cap.read()
            # mirror frame
            # frame = cv2.flip(frame, 1)
            # update landmarker results
            detector.detect_async(frame)

            frame = detector.draw(frame)
            # display image
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) == ord("q"):
                break

        # release everything
        detector.close()
        cap.release()
        cv2.destroyAllWindows()
