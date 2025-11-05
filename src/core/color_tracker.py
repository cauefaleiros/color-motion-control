import cv2
import numpy as np

BLUE_LOWER = np.array([100, 150, 0])
BLUE_UPPER = np.array([140, 255, 255])

RED_LOWER_1 = np.array([0, 150, 50])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 150, 50])
RED_UPPER_2 = np.array([180, 255, 255])

def get_color_mask(hsv_frame, lower, upper):
    return cv2.inRange(hsv_frame, lower, upper)

def get_largest_contour_center(mask, min_area=300):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < min_area:
        return None
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def detect_bracelets(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask_blue = get_color_mask(hsv, BLUE_LOWER, BLUE_UPPER)
    center_blue = get_largest_contour_center(mask_blue)

    mask_red1 = get_color_mask(hsv, RED_LOWER_1, RED_UPPER_1)
    mask_red2 = get_color_mask(hsv, RED_LOWER_2, RED_UPPER_2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    center_red = get_largest_contour_center(mask_red)

    return center_blue, center_red, mask_blue, mask_red