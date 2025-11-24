import logging
import time

import cv2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VideoStream:
    def __init__(self, src=1, width=640, height=480):
        print(f"Abrindo câmera com ID: {src}")
        self.cap = cv2.VideoCapture(src)
        time.sleep(0.5)
        if not self.cap.isOpened():
            logging.error(f"ERRO: Não foi possível abrir a câmera com ID {src}")
            raise RuntimeError(f"Falha ao abrir a câmera com ID {src}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        for _ in range(5):
            self.cap.read()
        logging.info(f"Câmera {src} inicializada com sucesso em {width}x{height}")

    def read(self):
        if not self.cap or not self.cap.isOpened():
            logging.warning("Câmera não está aberta para leitura.")
            return None
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logging.warning("Falha ao ler frame da câmera.")
            return None
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            logging.info("Câmera liberada.")

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()
