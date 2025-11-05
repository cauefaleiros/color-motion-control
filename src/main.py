from core.video_stream import VideoStream
from core.color_tracker import detect_bracelets
from core.gesture_mapper import map_gesture
from core.input_emulator import press_command
import cv2

vs = VideoStream()
if not vs.is_opened():
    print("Erro ao abrir webcam!")
    exit()

while True:
    frame = vs.read()
    if frame is None:
        break

    center_blue, center_red, mask_blue, mask_red = detect_bracelets(frame)

    if center_blue:
        cv2.circle(frame, center_blue, 15, (255, 0, 0), 3)
    if center_red:
        cv2.circle(frame, center_red, 15, (0, 0, 255), 3)

    cmd_blue = map_gesture(center_blue, frame.shape, 'blue')
    cmd_red = map_gesture(center_red, frame.shape, 'red')

    print(f"Comando azul: {cmd_blue}, Comando vermelho: {cmd_red}")

    if cmd_blue:
        press_command(cmd_blue)
    if cmd_red:
        press_command(cmd_red)

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.release()
cv2.destroyAllWindows()
