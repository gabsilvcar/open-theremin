# from hand_detection import Detector, Webcam
from hand_detection_classic import DetectorClassic, WebcamClassic

# detector = Detector()
# webcam = Webcam(detector)

detector = DetectorClassic()
webcam = WebcamClassic(detector)
