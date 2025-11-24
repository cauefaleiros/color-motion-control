# commit
import cv2
import numpy as np


class ColorCalibration:
    def __init__(self):
        self.current_color = None
        self.current_limits = {
            "lower": np.array([0, 0, 0]),
            "upper": np.array([179, 255, 255]),
        }
        self.calibrated_ranges = {
            "blue_lower": [100, 50, 50],
            "blue_upper": [130, 255, 255],
            "red_lower_1": [0, 50, 50],
            "red_upper_1": [10, 255, 255],
            "red_lower_2": [170, 50, 50],
            "red_upper_2": [180, 255, 255],
        }

    def nothing(self, x):
        pass

    def create_trackbar_window(self, color_name):
        window_name = f"Calibracao - {color_name}"
        cv2.namedWindow(window_name)
        cv2.createTrackbar(
            "H Min", window_name, self.current_limits["lower"][0], 179, self.nothing
        )
        cv2.createTrackbar(
            "S Min", window_name, self.current_limits["lower"][1], 255, self.nothing
        )
        cv2.createTrackbar(
            "V Min", window_name, self.current_limits["lower"][2], 255, self.nothing
        )
        cv2.createTrackbar(
            "H Max", window_name, self.current_limits["upper"][0], 179, self.nothing
        )
        cv2.createTrackbar(
            "S Max", window_name, self.current_limits["upper"][1], 255, self.nothing
        )
        cv2.createTrackbar(
            "V Max", window_name, self.current_limits["upper"][2], 255, self.nothing
        )

    def update_limits_from_trackbar(self, window_name):
        h_min = cv2.getTrackbarPos("H Min", window_name)
        s_min = cv2.getTrackbarPos("S Min", window_name)
        v_min = cv2.getTrackbarPos("V Min", window_name)
        h_max = cv2.getTrackbarPos("H Max", window_name)
        s_max = cv2.getTrackbarPos("S Max", window_name)
        v_max = cv2.getTrackbarPos("V Max", window_name)
        self.current_limits["lower"] = np.array([h_min, s_min, v_min])
        self.current_limits["upper"] = np.array([h_max, s_max, v_max])

    def run_single_calibration(self, cap, color_name):
        print(
            f"Calibrando {color_name}. Posicione o objeto colorido na webcam e pressione 'c' para confirmar."
        )
        window_name = f"Calibracao - {color_name}"
        self.create_trackbar_window(color_name)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro ao ler da câmera durante calibração.")
                break

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            self.update_limits_from_trackbar(window_name)

            mask = cv2.inRange(
                hsv, self.current_limits["lower"], self.current_limits["upper"]
            )
            result = cv2.bitwise_and(frame, frame, mask=mask)

            cv2.imshow(window_name, result)
            cv2.imshow("Calibracao - Original", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                print(f"Calibração para {color_name} concluída.")
                cv2.destroyWindow(window_name)
                cv2.destroyWindow("Calibracao - Original")
                return self.current_limits["lower"], self.current_limits["upper"]
            elif key == 27:  # ESC
                print("Calibração cancelada.")
                cv2.destroyWindow(window_name)
                cv2.destroyWindow("Calibracao - Original")
                return None, None

        cv2.destroyAllWindows()
        return None, None

    def run_full_calibration(self, cap):
        print("--- INICIANDO CALIBRAÇÃO ---")
        print("Este processo resolve o problema de interferência de iluminação.")
        print("-----------------------------")

        blue_lower, blue_upper = self.run_single_calibration(cap, "AZUL")
        if blue_lower is None or blue_upper is None:
            print("Calibração AZUL cancelada ou falhou. Usando valores padrão.")
            blue_lower = np.array(self.calibrated_ranges["blue_lower"])
            blue_upper = np.array(self.calibrated_ranges["blue_upper"])

        red_lower_1, red_upper_1 = self.run_single_calibration(cap, "VERMELHO Faixa 1")
        if red_lower_1 is None or red_upper_1 is None:
            print(
                "Calibração VERMELHO Faixa 1 cancelada ou falhou. Usando valores padrão."
            )
            red_lower_1 = np.array(self.calibrated_ranges["red_lower_1"])
            red_upper_1 = np.array(self.calibrated_ranges["red_upper_1"])

        red_lower_2, red_upper_2 = self.run_single_calibration(cap, "VERMELHO Faixa 2")
        if red_lower_2 is None or red_upper_2 is None:
            print(
                "Calibração VERMELHO Faixa 2 cancelada ou falhou. Usando valores padrão."
            )
            red_lower_2 = np.array(self.calibrated_ranges["red_lower_2"])
            red_upper_2 = np.array(self.calibrated_ranges["red_upper_2"])

        print("--- CALIBRAÇÃO CONCLUÍDA ---")
        return {
            "blue_lower": blue_lower,
            "blue_upper": blue_upper,
            "red_lower_1": red_lower_1,
            "red_upper_1": red_upper_1,
            "red_lower_2": red_lower_2,
            "red_upper_2": red_upper_2,
        }
