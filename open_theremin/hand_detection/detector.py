import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe import ImageFormat
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Detector:
    def __init__(self):
        self.result = mp.tasks.vision.HandLandmarkerResult
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.createLandmarker()

    def createLandmarker(self):
        # callback function
        def update_result(
            result: mp.tasks.vision.HandLandmarkerResult,
            output_image: mp.Image,
            timestamp_ms: int,
        ):
            self.result = result

        # HandLandmarkerOptions (details here: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker/python#live-stream)
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path="model/hand_landmarker.task"
            ),  # path to model
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # running on a live stream
            num_hands=2,  # track both hands
            min_hand_detection_confidence=0.3,  # lower than value to get predictions more often
            min_hand_presence_confidence=0.3,  # lower than value to get predictions more often
            min_tracking_confidence=0.3,  # lower than value to get predictions more often
            result_callback=update_result,
        )

        # initialize landmarker
        self.landmarker = self.landmarker.create_from_options(options)

    def detect_async(self, frame):
        # convert np frame to mp image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        # detect landmarks
        self.landmarker.detect_async(
            image=mp_image, timestamp_ms=int(time.time() * 1000)
        )

    def close(self):
        # close landmarker
        self.landmarker.close()

    def draw(self, frame, detections):
        # draw landmarks on frame
        frame = draw_landmarks_on_image(frame, self.result)
        # count number of fingers raised
        # frame = count_fingers_raised(frame, self.result)
        return frame

    def hand_pos(self, detections):
        return get_hand_pos(self.result)


def get_hand_pos(detection_result):
    try:
        if detection_result.hand_landmarks == []:
            return 0, 0
        else:
            hand_landmarks_list = detection_result.hand_landmarks
            for idx in range(len(hand_landmarks_list)):
                if detection_result.handedness[idx][0].category_name == "Right":
                    # hand landmarks is a list of landmarks where each entry in the list has an x, y, and z in normalized image coordinates
                    hand_landmarks = hand_landmarks_list[idx]
                    return hand_landmarks[0].x, hand_landmarks[0].y
            return 0, 0
    except:
        return 0, 0


def draw_landmarks_on_image(
    rgb_image, detection_result: mp.tasks.vision.HandLandmarkerResult
):
    """Courtesy of https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb"""
    try:
        if detection_result.hand_landmarks == []:
            return rgb_image
        else:
            hand_landmarks_list = detection_result.hand_landmarks
            handedness_list = detection_result.handedness
            annotated_image = np.copy(rgb_image)

            # Loop through the detected hands to visualize.
            for idx in range(len(hand_landmarks_list)):
                hand_landmarks = hand_landmarks_list[idx]

                # Draw the hand landmarks.
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend(
                    [
                        landmark_pb2.NormalizedLandmark(
                            x=landmark.x, y=landmark.y, z=landmark.z
                        )
                        for landmark in hand_landmarks
                    ]
                )
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    hand_landmarks_proto,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style(),
                )

            return annotated_image
    except:
        return rgb_image


def count_fingers_raised(
    rgb_image, detection_result: mp.tasks.vision.HandLandmarkerResult
):
    """Iterate through each hand, checking if fingers (and thumb) are raised.
    Hand landmark enumeration (and weird naming convention) comes from
    https://developers.google.com/mediapipe/solutions/vision/hand_landmarker."""
    try:
        # Get Data
        hand_landmarks_list = detection_result.hand_landmarks
        # Counter
        numRaised = 0
        # for each hand...
        for idx in range(len(hand_landmarks_list)):
            # hand landmarks is a list of landmarks where each entry in the list has an x, y, and z in normalized image coordinates
            hand_landmarks = hand_landmarks_list[idx]
            # for each fingertip... (hand_landmarks 4, 8, 12, and 16)
            for i in range(8, 21, 4):
                # make sure finger is higher in image the 3 proceeding values (2 finger segments and knuckle)
                tip_y = hand_landmarks[i].y
                dip_y = hand_landmarks[i - 1].y
                pip_y = hand_landmarks[i - 2].y
                mcp_y = hand_landmarks[i - 3].y
                if tip_y < min(dip_y, pip_y, mcp_y):
                    numRaised += 1
            # for the thumb
            # use direction vector from wrist to base of thumb to determine "raised"
            tip_x = hand_landmarks[4].x
            dip_x = hand_landmarks[3].x
            pip_x = hand_landmarks[2].x
            mcp_x = hand_landmarks[1].x
            palm_x = hand_landmarks[0].x
            if mcp_x > palm_x:
                if tip_x > max(dip_x, pip_x, mcp_x):
                    numRaised += 1
            else:
                if tip_x < min(dip_x, pip_x, mcp_x):
                    numRaised += 1

        # display number of fingers raised on the image
        annotated_image = np.copy(rgb_image)
        height, width, _ = annotated_image.shape
        text_x = int(hand_landmarks[0].x * width) - 100
        text_y = int(hand_landmarks[0].y * height) + 50
        cv2.putText(
            img=annotated_image,
            text=str(numRaised) + " Fingers Raised",
            org=(text_x, text_y),
            fontFace=cv2.FONT_HERSHEY_DUPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=2,
            lineType=cv2.LINE_4,
        )
        return annotated_image
    except:
        return rgb_image
