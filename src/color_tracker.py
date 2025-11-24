# commit
from collections import deque

import cv2
import numpy as np


class ColorTracker:
    def __init__(self):
        # Valores padrão HSV para azul (ajustáveis via calibração)
        self.blue_lower = np.array([100, 150, 50])
        self.blue_upper = np.array([130, 255, 255])

        # Valores padrão HSV para vermelho (duas faixas para lidar com wrap-around)
        self.red_lower_1 = np.array([0, 150, 50])
        self.red_upper_1 = np.array([10, 255, 255])
        self.red_lower_2 = np.array([170, 150, 50])
        self.red_upper_2 = np.array([180, 255, 255])

        # Filas para suavização temporal (média móvel)
        self.smoothing_frames = 5
        self.blue_positions = deque(maxlen=self.smoothing_frames)
        self.red_positions = deque(maxlen=self.smoothing_frames)

        self.min_area = 300  # Área mínima para considerar um contorno válido

    def update_blue_range(self, lower, upper):
        """Atualiza os limites HSV para cor azul (implementa a calibração)."""
        self.blue_lower = np.array(lower)
        self.blue_upper = np.array(upper)

    def update_red_range(self, lower1, upper1, lower2, upper2):
        """Atualiza os limites HSV para cor vermelha (implementa a calibração)."""
        self.red_lower_1 = np.array(lower1)
        self.red_upper_1 = np.array(upper1)
        self.red_lower_2 = np.array(lower2)
        self.red_upper_2 = np.array(upper2)

    def detect_bracelets(self, frame):
        """
        Detecta pulseiras azul e vermelha no frame.
        Aplica conversão HSV, máscara, remoção de ruído, detecção de contornos e suavização.
        """
        # Aplica filtro Gaussiano para suavizar ruídos (mencionado na dissertação)
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)

        # Converte o frame para o espaço de cores HSV
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # --- Detecção AZUL ---
        mask_blue = cv2.inRange(hsv, self.blue_lower, self.blue_upper)
        # Aplica operações morfológicas para remover ruídos
        kernel = np.ones((5, 5), np.uint8)
        mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
        mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)

        # Encontra contornos na máscara azul
        contours_blue, _ = cv2.findContours(
            mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        largest_blue_contour = None
        center_blue_raw = None
        if contours_blue:
            # Encontra o maior contorno que satisfaça a área mínima
            largest_blue_contour = max(contours_blue, key=cv2.contourArea)
            if cv2.contourArea(largest_blue_contour) >= self.min_area:
                # Calcula o centroide
                M = cv2.moments(largest_blue_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    center_blue_raw = (cx, cy)
            else:
                largest_blue_contour = None  # Descarta contorno pequeno

        # Suaviza a posição azul
        center_blue = self.smooth_position(center_blue_raw, self.blue_positions)

        # --- Detecção VERMELHO ---
        mask_red1 = cv2.inRange(hsv, self.red_lower_1, self.red_upper_1)
        mask_red2 = cv2.inRange(hsv, self.red_lower_2, self.red_upper_2)
        mask_red_full = mask_red1 | mask_red2  # Combina as duas máscaras do vermelho

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

        # Suaviza a posição vermelha
        center_red = self.smooth_position(center_red_raw, self.red_positions)

        return {
            "blue_center": center_blue,
            "red_center": center_red,
            "blue_mask": mask_blue,
            "red_mask": mask_red_full,
            "blue_contour": largest_blue_contour,
            "red_contour": largest_red_contour,
            "blue_raw_center": center_blue_raw,  # Útil para debug ou calibração
            "red_raw_center": center_red_raw,  # Útil para debug ou calibração
        }

    def smooth_position(self, new_position, positions_queue):
        """
        Aplica suavização temporal (média móvel) para resolver
        problemas de movimentos falsos e sensibilidade excessiva.
        """
        if new_position is None:
            # Se não detectar, limpa a fila para não influenciar futuros movimentos
            positions_queue.clear()
            return None

        positions_queue.append(new_position)

        # Calcula a média das últimas N posições suavizadas
        if len(positions_queue) > 0:
            avg_x = int(np.mean([pos[0] for pos in positions_queue]))
            avg_y = int(np.mean([pos[1] for pos in positions_queue]))
            return (avg_x, avg_y)

        return new_position

    def draw_detection(self, frame, detection_data):
        """
        Desenha os resultados da detecção no frame para visualização.
        """
        result = frame.copy()

        # Desenha contorno e centro para pulseira AZUL
        if detection_data["blue_contour"] is not None and detection_data["blue_center"]:
            cv2.drawContours(
                result, [detection_data["blue_contour"]], -1, (255, 0, 0), 2
            )
            cv2.circle(result, detection_data["blue_center"], 10, (255, 0, 0), -1)
            cv2.putText(
                result,
                "AZUL",
                (
                    detection_data["blue_center"][0] - 30,
                    detection_data["blue_center"][1] - 20,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2,
            )

        # Desenha contorno e centro para pulseira VERMELHA
        if detection_data["red_contour"] is not None and detection_data["red_center"]:
            cv2.drawContours(
                result, [detection_data["red_contour"]], -1, (0, 0, 255), 2
            )
            cv2.circle(result, detection_data["red_center"], 10, (0, 0, 255), -1)
            cv2.putText(
                result,
                "VERMELHO",
                (
                    detection_data["red_center"][0] - 40,
                    detection_data["red_center"][1] - 20,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        return result
