"""
Script para encontrar o ID correto da câmera (DroidCam)
"""

import sys

import cv2


def test_camera(camera_id):
    """Testa um ID de câmera"""
    print(f"\n{'=' * 50}")
    print(f"Testando Camera ID: {camera_id}")
    print("=" * 50)

    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"❌ Câmera {camera_id} não pode ser aberta")
        return False

    print(f"✓ Câmera {camera_id} abriu!")

    # Tenta capturar um frame
    ret, frame = cap.read()

    if not ret or frame is None:
        print(f"❌ Câmera {camera_id} não captura frames")
        cap.release()
        return False

    print(f"✓ Frame capturado: {frame.shape}")
    print(f"✓ CÂMERA {camera_id} FUNCIONA!")

    # Mostra a imagem
    print("\nPressione qualquer tecla para testar próxima câmera...")
    cv2.imshow(f"Camera {camera_id}", frame)
    cv2.waitKey(2000)  # Mostra por 2 segundos
    cv2.destroyAllWindows()

    cap.release()
    return True


def test_droidcam_ip():
    """Testa conexão direta por IP"""
    print("\n" + "=" * 50)
    print("TESTE DE CONEXÃO POR IP")
    print("=" * 50)
    print("\nSe souber o IP do DroidCam, digite-o agora.")
    print("Exemplo: 192.168.1.100")
    print("Ou pressione ENTER para pular")

    ip = input("\nIP do DroidCam: ").strip()

    if not ip:
        return False

    url = f"http://{ip}:4747/video"
    print(f"\nTentando conectar em: {url}")

    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print(f"❌ Não conectou em {url}")
        return False

    ret, frame = cap.read()

    if not ret or frame is None:
        print(f"❌ Conectou mas não captura frames")
        cap.release()
        return False

    print(f"✓ CONECTADO VIA IP!")
    print(f"✓ Frame: {frame.shape}")
    print(f"\n🎉 Use este URL no main.py:")
    print(f"   camera_id = '{url}'")

    cv2.imshow("DroidCam via IP", frame)
    print("\nPressione qualquer tecla para fechar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cap.release()
    return True


def main():
    print("\n" + "=" * 50)
    print("TESTE DE CÂMERAS - DROIDCAM")
    print("=" * 50)
    print("\nEste script vai testar diferentes IDs de câmera")
    print("para encontrar o DroidCam.")
    print("=" * 50)

    # Testa IDs de 0 a 5
    working_cameras = []

    for i in range(6):
        if test_camera(i):
            working_cameras.append(i)

    print("\n" + "=" * 50)
    print("RESULTADO DOS TESTES")
    print("=" * 50)

    if working_cameras:
        print(f"\n✓ Câmeras funcionando: {working_cameras}")
        print(f"\n🎯 Use este valor no main.py:")
        for cam_id in working_cameras:
            print(f"   camera_id = {cam_id}")
    else:
        print("\n❌ Nenhuma câmera funcionou nos IDs 0-5")
        print("\nVamos tentar por IP...")
        test_droidcam_ip()

    print("\n" + "=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(0)
