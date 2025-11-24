# commit
import sys
import time

import cv2

from calibration import ColorCalibration
from color_tracker import ColorTracker
from gesture_mapper import GestureMapper
from input_emulator import press_command
from video_stream import VideoStream


class GestureControlSystem:
    def __init__(self):
        self.video = None
        self.tracker = ColorTracker()
        self.mapper = GestureMapper()
        self.calibration = ColorCalibration()
        self.running = False
        self.show_masks = False
        self.show_zones = True

    def initialize_camera(self, camera_id=0, width=640, height=480):
        print("Inicializando câmera...")
        try:
            self.video = VideoStream(src=camera_id, width=width, height=height)
        except RuntimeError as e:
            print(e)
            return False
        print("✓ Câmera inicializada com sucesso!")
        return True

    def run_calibration(self):
        if self.video is None:
            print("ERRO: Câmera não inicializada!")
            return False

        print("\n" + "=" * 70)
        print("INICIANDO CALIBRAÇÃO")
        print("=" * 70)
        print("Siga as instruções na janela da câmera.")
        print("Este processo resolve o problema de interferência de iluminação.")
        print("=" * 70 + "\n")

        ranges = self.calibration.run_full_calibration(self.video.cap)

        if ranges:
            self.tracker.update_blue_range(ranges["blue_lower"], ranges["blue_upper"])
            self.tracker.update_red_range(
                ranges["red_lower_1"],
                ranges["red_upper_1"],
                ranges["red_lower_2"],
                ranges["red_upper_2"],
            )
            print("✓ Sistema calibrado com sucesso!")
            return True
        else:
            print("✗ Calibração falhou ou foi cancelada.")
            return False

    def display_help(self):
        print("\n" + "=" * 70)
        print("INSTRUÇÕES DE USO")
        print("=" * 70)
        print("PULSEIRA AZUL (Mão Esquerda):")
        print("  - Topo: W (Mover para Cima)")
        print("  - Baixo: S (Mover para Baixo)")
        print("  - Esquerda: A (Mover para Esquerda)")
        print("  - Direita: D (Mover para Direita)")
        print()
        print("PULSEIRA VERMELHA (Mão Direita):")
        print("  - Topo: X (Ação 1)")
        print("  - Baixo: Y (Ação 2)")
        print("  - Esquerda: B (Ação 3)")
        print("  - Direita: Z (Ação 4)")
        print()
        print("TECLAS DE CONTROLE:")
        print("  M - Mostrar/Ocultar Máscaras de Detecção")
        print("  Z - Mostrar/Ocultar Zonas de Controle")
        print("  H - Mostrar esta ajuda")
        print("  ESC - Sair do sistema")
        print("=" * 70 + "\n")

    def draw_status(self, frame, blue_cmd, red_cmd, fps):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        cv2.putText(
            frame,
            "Sistema de Controle por Gestos (APS)",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (frame.shape[1] - 120, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
        blue_text = f"AZUL: {blue_cmd if blue_cmd else '---'}"
        red_text = f"VERMELHO: {red_cmd if red_cmd else '---'}"
        cv2.putText(
            frame, blue_text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2
        )
        cv2.putText(
            frame, red_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2
        )
        cv2.putText(
            frame,
            "M: Mascaras | Z: Zonas | H: Ajuda | ESC: Sair",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        return frame

    def run(self):
        self.running = True
        self.display_help()
        print("Sistema iniciado! Posicione as pulseiras e comece a jogar!")
        print("Pressione ESC para sair.\n")

        prev_time = time.time()
        fps = 0

        while self.running:
            frame = self.video.read()
            if frame is None:
                print("ERRO: Falha ao capturar frame!")
                break

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
                print(
                    f"-> AZUL: {blue_cmd} ({self.mapper.get_command_description(blue_cmd)})"
                )
            if red_cmd:
                press_command(red_cmd)
                print(
                    f"-> VERMELHO: {red_cmd} ({self.mapper.get_command_description(red_cmd)})"
                )

            display_frame = self.draw_status(display_frame, blue_cmd, red_cmd, fps)

            cv2.imshow("Controle por Gestos - APS", display_frame)

            if self.show_masks:
                cv2.imshow("Mascara AZUL", detection["blue_mask"])
                cv2.imshow("Mascara VERMELHO", detection["red_mask"])
            else:
                cv2.destroyWindow("Mascara AZUL")
                cv2.destroyWindow("Mascara VERMELHO")

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("\nEncerrando sistema...")
                self.running = False
            elif key == ord("m") or key == ord("M"):
                self.show_masks = not self.show_masks
                print(f"Mascaras {'ativadas' if self.show_masks else 'desativadas'}")
            elif key == ord("z") or key == ord("Z"):
                self.show_zones = not self.show_zones
                print(f"Zonas {'ativadas' if self.show_zones else 'desativadas'}")
            elif key == ord("h") or key == ord("H"):
                self.display_help()

        self.cleanup()

    def cleanup(self):
        print("Liberando recursos...")
        if self.video:
            self.video.release()
        cv2.destroyAllWindows()
        print("✓ Sistema encerrado!")


def main():
    print("\n" + "=" * 70)
    print("SISTEMA DE CONTROLE POR MOVIMENTO COM DETECÇÃO DE CORES - APS")
    print("=" * 70)
    print("Desenvolvido para APS - Processamento de Imagem - UNIP")
    print("=" * 70 + "\n")

    system = GestureControlSystem()

    if not system.initialize_camera(camera_id=0, width=640, height=480):
        print("Não foi possível inicializar o sistema.")
        return 1

    response = (
        input("\nDeseja executar a calibração das cores? (S/n): ").strip().upper()
    )
    if response != "N":
        if not system.run_calibration():
            print("Continuando com valores padrão...")

    input("\nPressione ENTER para iniciar o sistema...")

    try:
        system.run()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        system.cleanup()
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback

        traceback.print_exc()
        system.cleanup()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
