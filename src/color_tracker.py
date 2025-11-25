from collections import deque

import cv2
import numpy as np


class ColorTracker:
    def __init__(self):
        # Intervalo azul ajustado para capturar diferentes tons de azul
        self.blue_lower = np.array([90, 80, 50])
        self.blue_upper = np.array([140, 255, 255])

        # Intervalo vermelho (duas faixas)
        self.red_lower_1 = np.array([0, 150, 50])
        self.red_upper_1 = np.array([10, 255, 255])
        self.red_lower_2 = np.array([170, 150, 50])
        self.red_upper_2 = np.array([180, 255, 255])

        self.smoothing_frames = 5
        self.blue_positions = deque(maxlen=self.smoothing_frames)
        self.red_positions = deque(maxlen=self.smoothing_frames)
        self.min_area = 300

    def update_blue_range(self, lower, upper):
        self.blue_lower = np.array(lower)
        self.blue_upper = np.array(upper)

    def update_red_range(self, lower1, upper1, lower2, upper2):
        self.red_lower_1 = np.array(lower1)
        self.red_upper_1 = np.array(upper1)
        self.red_lower_2 = np.array(lower2)
        self.red_upper_2 = np.array(upper2)

    def detect_bracelets(self, frame):
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # --- DETECÇÃO AZUL ---
        mask_blue = cv2.inRange(hsv, self.blue_lower, self.blue_upper)
        kernel = np.ones((5, 5), np.uint8)
        mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
        mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)

        contours_blue, _ = cv2.findContours(
            mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        largest_blue_contour = None
        center_blue_raw = None
        if contours_blue:
            largest_blue_contour = max(contours_blue, key=cv2.contourArea)
            if cv2.contourArea(largest_blue_contour) >= self.min_area:
                M = cv2.moments(largest_blue_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    center_blue_raw = (cx, cy)
                else:
                    largest_blue_contour = None
        center_blue = self.smooth_position(center_blue_raw, self.blue_positions)

        # --- DETECÇÃO VERMELHO ---
        mask_red1 = cv2.inRange(hsv, self.red_lower_1, self.red_upper_1)
        mask_red2 = cv2.inRange(hsv, self.red_lower_2, self.red_upper_2)
        mask_red_full = cv2.bitwise_or(mask_red1, mask_red2)
        mask_red_full = cv2.morphologyEx(mask_red_full, cv2.MORPH_OPEN, kernel)
        mask_red_full = cv2.morphologyEx(mask_red_full, cv2.MORPH_CLOSE, kernel)

        contours_red, _ = cv2.findContours(
            mask_red_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        largest_red_contour = None
        center_red_raw = None
        if contours_red:
            largest_red_contour = max(contours_red, key=cv2.contourArea)
            if cv2.contourArea(largest_red_contour) >= self.min_area:
                M = cv2.moments(largest_red_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    center_red_raw = (cx, cy)
                else:
                    largest_red_contour = None
        center_red = self.smooth_position(center_red_raw, self.red_positions)

        return {
            "blue_center": center_blue,
            "red_center": center_red,
            "blue_mask": mask_blue,
            "red_mask": mask_red_full,
            "blue_contour": largest_blue_contour,
            "red_contour": largest_red_contour,
            "blue_raw_center": center_blue_raw,
            "red_raw_center": center_red_raw,
        }

    def smooth_position(self, new_position, positions_queue):
        if new_position is None:
            positions_queue.clear()
            return None
        positions_queue.append(new_position)
        if len(positions_queue) > 0:
            avg_x = int(np.mean([pos[0] for pos in positions_queue]))
            avg_y = int(np.mean([pos[1] for pos in positions_queue]))
            return (avg_x, avg_y)
        return new_position

    def draw_detection(self, frame, detection_data):
        result = frame.copy()
        if detection_data["blue_contour"] is not None and detection_data["blue_center"]:
            cv2.drawContours(
                result, [detection_data["blue_contour"]], -1, (255, 0, 0), 2
            )
            cv2.circle(result, detection_data["blue_center"], 10, (255, 0, 0), -1)
        if detection_data["red_contour"] is not None and detection_data["red_center"]:
            cv2.drawContours(
                result, [detection_data["red_contour"]], -1, (0, 0, 255), 2
            )
            cv2.circle(result, detection_data["red_center"], 10, (0, 0, 255), -1)
        return result


# --- TESTE RÁPIDO ---
if __name__ == "__main__":
    tracker = ColorTracker()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detection = tracker.detect_bracelets(frame)
        output = tracker.draw_detection(frame, detection)
        cv2.imshow("Detecção", output)
        cv2.imshow("Máscara Azul", detection["blue_mask"])
        cv2.imshow("Máscara Vermelha", detection["red_mask"])
        if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
            break
    cap.release()
    cv2.destroyAllWindows()
