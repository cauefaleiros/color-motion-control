# commit
import logging

import cv2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoStream:
    def __init__(self, src=2, width=640, height=480):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            logging.error(f"Falha ao abrir a câmera com ID {src}")
            raise RuntimeError(f"Falha ao abrir a câmera com ID {src}")

        # Define resolução para otimizar performance (mencionado na dissertação)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        logging.info(f"Câmera configurada: {width}x{height}")

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            logging.warning("Falha ao ler frame da câmera.")
            return None
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            logging.info("Câmera liberada.")

    def is_opened(self):
        return self.cap.isOpened()
