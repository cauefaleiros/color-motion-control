"""
Teste rápido do DroidCam
"""

import sys

import cv2

# SEU IP DO DROIDCAM
DROIDCAM_URL = "http://192.168.15.6:4747/video"

print("=" * 60)
print("TESTE DO DROIDCAM")
print("=" * 60)
print(f"URL: {DROIDCAM_URL}")
print("\nTentando conectar...")

# Tenta abrir
cap = cv2.VideoCapture(DROIDCAM_URL)

if not cap.isOpened():
    print("❌ NÃO CONSEGUIU ABRIR!")
    print("\nVerifique:")
    print("1. DroidCam está aberto no celular")
    print("2. Está na mesma rede Wi-Fi")
    print("3. O IP está correto")
    sys.exit(1)

print("✓ Câmera abriu!")

# Descarta primeiros frames
for i in range(10):
    ret, frame = cap.read()
    print(f"Frame {i}: ret={ret}, frame={'OK' if frame is not None else 'None'}")

print("\nTestando captura contínua...")
print("Pressione 'q' para sair\n")

frame_count = 0
while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print(f"❌ Erro no frame {frame_count}")
        continue

    frame_count += 1

    # Mostra info
    cv2.putText(
        frame,
        f"Frame: {frame_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )
    cv2.putText(
        frame,
        f"Shape: {frame.shape}",
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )
    cv2.putText(
        frame,
        "Pressione 'q' para sair",
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.imshow("Teste DroidCam", frame)

    if frame_count % 30 == 0:
        print(f"✓ {frame_count} frames capturados")

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

print(f"\n✓ Total: {frame_count} frames capturados")
print("✓ DroidCam funcionando!")

cap.release()
cv2.destroyAllWindows()
