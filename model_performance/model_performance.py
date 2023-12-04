from pathlib import Path

import cv2

SHOW_BBS = False
COLOR_GT = (0, 100, 255)  # Orange
COLOR_DETECTED = (255, 150, 0)  # Blue
COLOR_INTERSECTIONS = (150, 255, 0)  # Green

IOU_THRESH = 0.5

PATH_TEST_IMGS = Path(__file__).parents[1] / "Dataset_open_theremin" / "test"
PATH_GT_BBS_POS = PATH_TEST_IMGS / "pos.txt"  # Path ground truth bounding boxes
PATH_GT_BBS_NEG = PATH_TEST_IMGS / "neg.txt"  # Path ground truth bounding boxes
PATH_MODEL = Path(__file__).parents[1] / "model" / "cascade.xml"


def draw(image, detections, color):
    # Draw on the frame the two detected objects most likely to be hands
    for x, y, w, h in detections:
        image = cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

    return image


# coor being x or y and size being width or height
def intersectionAxis(coord1, size1, coord2, size2):
    coordi = 0
    sizei = 0

    if (
        coord1 < coord2 and coord2 < coord1 + size1
    ):  # coord2 is in ground truth area in the axis
        coordi = coord2
        if coord2 + size2 > coord1 + size1:
            sizei = coord1 + size1 - coord2
        else:
            sizei = size2
    elif (
        coord1 < coord2 + size2 and coord2 + size2 < coord1 + size1
    ):  # coord2+size2 is in ground truth area in the axis
        if coord2 > coord1:
            coordi = coord2
        else:
            coordi = coord1
        sizei = coord2 + size2 - coordi
    elif (
        coord2 < coord1 and coord1 < coord2 + size2
    ):  # coord1 is in detected area in the axis
        coordi = coord1
        if coord1 + size1 > coord2 + size2:
            sizei = coord2 + size2 - coord1
        else:
            sizei = size1
    elif (
        coord2 < coord1 + size1 and coord1 + size1 < coord2 + size2
    ):  # coord1+size1 is in detected area in the axis
        if coord1 > coord2:
            coordi = coord1
        else:
            coordi = coord2
        sizei = coord1 + size1 - coordi

    return (coordi, sizei)


if __name__ == "__main__":
    cascade_class = cv2.CascadeClassifier()
    cascade_class.load((str)(PATH_MODEL))

    tp_all = 0
    fp_all = 0
    fn_all = 0
    for path_set in [PATH_GT_BBS_POS, PATH_GT_BBS_NEG]:
        with path_set.open() as file:
            for line in file.readlines():
                img_name = line.split()[0]
                num_bbs = 0
                if len(line.split()) > 1:
                    num_bbs = (int)(line.split()[1])

                # Get ground truth coordinates
                bbs_list: list = []
                for i in range(num_bbs):
                    x, y, w, h = line.split()[2 + i * 4 : 2 + i * 4 + 4]
                    x = (int)(x)
                    y = (int)(y)
                    w = (int)(w)
                    h = (int)(h)
                    bbs_list.append((x, y, w, h))

                # Image reading and preparation
                img_path = PATH_TEST_IMGS / img_name
                image = cv2.imread((str)(img_path))
                img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                img_gray = cv2.equalizeHist(img_gray)

                # Detection of hands
                detections = cascade_class.detectMultiScale(image)

                # Calculate and show True Positives, False Positives, and False Negatives
                tp = 0
                fp = 0
                fn = 0
                intersections: list = []
                tps_gt: list = []
                tps_det: list = []
                if num_bbs > 0:
                    for x1, y1, w1, h1 in bbs_list:
                        gt_area = w1 * h1
                        for x2, y2, w2, h2 in detections:
                            if (x2, y2, w2, h2) in tps_det:
                                pass

                            det_area = w2 * h2
                            xi, wi = intersectionAxis(x1, w1, x2, w2)
                            yi, hi = intersectionAxis(y1, h1, y2, h2)

                            intersection_area = wi * hi

                            iou = intersection_area / (
                                gt_area + det_area - intersection_area
                            )

                            if iou >= IOU_THRESH:
                                intersections.append((xi, yi, wi, hi))
                                tp += 1
                                tps_gt.append((x1, y1, w1, h1))
                                tps_det.append((x2, y2, w2, h2))
                                break
                    fp = len(detections) - len(tps_det)
                    fn = len(bbs_list) - len(tps_gt)
                else:
                    fp = len(detections)

                if SHOW_BBS:
                    print("TP: " + (str)(tp))
                    print("FP: " + (str)(fp))
                    print("FN: " + (str)(fn) + "\n")

                # Calculate total do True Positives, False Positives, and False Negatives
                tp_all += tp
                fp_all += fp
                fn_all += fn

                # Draw ground truth and detected bounding boxes and intersections of True Positives found
                if SHOW_BBS:
                    img_rect = draw(image, bbs_list, COLOR_GT)
                    img_rect = draw(img_rect, detections, COLOR_DETECTED)
                    img_rect = draw(img_rect, intersections, COLOR_INTERSECTIONS)
                    cv2.imshow("Detections", img_rect)
                    key = cv2.waitKey()
                    if key == ord("q"):
                        break
                    elif key == ord("n"):
                        continue

    # Calculate and show metrics of performance of the model
    precision = tp_all / (tp_all + fp_all)
    recall = tp_all / (tp_all + fn_all)
    f1_score = (2 * precision * recall) / (precision + recall)

    print("TP total: " + (str)(tp_all))
    print("FP total: " + (str)(fp_all))
    print("FN total: " + (str)(fn_all))
    print("Precision: " + (str)(precision))
    print("Recall: " + (str)(recall))
    print("F1 Score: " + (str)(f1_score))

    cv2.destroyAllWindows()
