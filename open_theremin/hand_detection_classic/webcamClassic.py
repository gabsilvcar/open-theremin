import cv2

class WebcamClassic:
    def __init__(self, detector):
        # access webcam
        cap = cv2.VideoCapture(0)

        while True:
            # pull frame
            ret, frame = cap.read()
            # update detections
            detections = detector.detect_async(frame)

            frame = detector.draw(frame, detections)
            # display image
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) == ord("q"):
                break

        # release everything
        cap.release()
        cv2.destroyAllWindows()