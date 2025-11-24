# commit
import cv2


def test_camera_ids(max_ids=10):
    print("Procurando câmeras...")
    available_cameras = []
    for i in range(max_ids):
        print(f"Testando câmera com ID {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"  ✓ Câmera ID {i} está disponível e funcional.")
                available_cameras.append(i)
            else:
                print(f"  ⚠ Câmera ID {i} está aberta, mas não consegue ler frames.")
            cap.release()
        else:
            print(f"  ✗ Câmera ID {i} NÃO está disponível.")
    return available_cameras


if __name__ == "__main__":
    cameras = test_camera_ids()
    print(f"\nCâmeras disponíveis encontradas: {cameras}")
    if cameras:
        print(
            f"Use um desses IDs no seu sistema (ex: Modifique video_stream.py para usar src={cameras[0]})."
        )
    else:
        print("Nenhuma câmera funcional foi encontrada.")
