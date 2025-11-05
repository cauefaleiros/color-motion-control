from core.color_tracker import detect_bracelets
from core.gesture_mapper import map_gesture
import cv2

# Inicializa webcam (usando OpenCV direto, sem VideoStream personalizado)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir webcam!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    center_blue, center_red, mask_blue, mask_red = detect_bracelets(frame)

    if center_blue:
        cv2.circle(frame, center_blue, 15, (255, 0, 0), 3)
    if center_red:
        cv2.circle(frame, center_red, 15, (0, 0, 255), 3)

    cmd_blue = map_gesture(center_blue, frame.shape, 'blue')
    cmd_red = map_gesture(center_red, frame.shape, 'red')

    print(f"Comando azul: {cmd_blue}, Comando vermelho: {cmd_red}")

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
