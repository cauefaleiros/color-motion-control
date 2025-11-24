import sys
import time
import traceback

import cv2

from color_tracker import ColorTracker
from gesture_mapper import GestureMapper
from input_emulator import press_command
from video_stream import VideoStream


class SimpleGestureControl:
    def __init__(self):
        self.video = None
        self.tracker = ColorTracker()
        self.mapper = GestureMapper()
        self.running = False
        self.show_zones = True

    def initialize_camera(self, camera_id=1, width=640, height=480):
        print("Inicializando câmera...")
        print(f"Tentando abrir câmera com ID: {camera_id}")
        try:
            self.video = VideoStream(src=camera_id, width=width, height=height)
        except RuntimeError as e:
            print(f"ERRO na inicialização: {e}")
            return False
        except Exception as e:
            print(f"ERRO inesperado na inicialização: {e}")
            traceback.print_exc()
            return False
        if not self.video.is_opened():
            print(
                "ERRO: O objeto VideoStream foi criado, mas a câmera não está aberta!"
            )
            return False
        test_frame = self.video.read()
        if test_frame is None:
            print("ERRO: Câmera abriu, mas não consegue capturar frames!")
            print("Tente outros IDs (0, 2, 3...) ou verifique os drivers da câmera.")
            return False
        print(f"✓ Câmera inicializada com sucesso! Frame shape: {test_frame.shape}")
        return True

    def run(self):
        self.running = True
        print("\n" + "=" * 60)
        print("SISTEMA INICIADO!")
        print("=" * 60)
        print("AZUL (esquerda): Cima=W | Baixo=S | Esq=A | Dir=D")
        print("VERMELHO (direita): X | Y | B | A")
        print("\nPressione ESC para sair\n")

        prev_time = time.time()
        fps = 0
        while self.running:
            frame = self.video.read()
            if frame is None:
                print("AVISO: Falha ao capturar frame! Tentando novamente...")
                time.sleep(0.1)
                continue
            current_time = time.time()
            if (current_time - prev_time) > 0:
                fps = 1 / (current_time - prev_time)
            prev_time = current_time
            detection = self.tracker.detect_bracelets(frame)
            display_frame = self.tracker.draw_detection(frame, detection)
            if self.show_zones:
                display_frame = self.mapper.draw_zones(display_frame)
            blue_cmd = self.mapper.map_gesture(
                detection["blue_center"], frame.shape, "blue"
            )
            red_cmd = self.mapper.map_gesture(
                detection["red_center"], frame.shape, "red"
            )
            if blue_cmd:
                press_command(blue_cmd)
            if red_cmd:
                press_command(red_cmd)
            cv2.imshow("Controle por Gestos", display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("\nEncerrando...")
                self.running = False

        self.cleanup()

    def cleanup(self):
        print("Liberando recursos...")
        if self.video:
            self.video.release()
        cv2.destroyAllWindows()
        print("✓ Sistema encerrado!")


def main():
    print("\n" + "=" * 60)
    print("CONTROLE POR GESTOS - SISTEMA SIMPLIFICADO")
    print("=" * 60)
    print("Detecta pulseiras azul e vermelha para controlar jogos")
    print("=" * 60 + "\n")
    system = SimpleGestureControl()
    camera_id = 1
    print(f"Conectando à câmera local com ID: {camera_id}")
    if not system.initialize_camera(camera_id=camera_id, width=640, height=480):
        print("\n⚠️ ERRO: Não conseguiu conectar à câmera local")
        print(" Verifique se a câmera está ligada e tente outros IDs.")
        return 1
    try:
        system.run()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        system.cleanup()
    except Exception as e:
        print(f"\nERRO inesperado no loop principal: {e}")
        traceback.print_exc()
        system.cleanup()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
