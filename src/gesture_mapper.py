import time

import cv2


class GestureMapper:
    """
    Mapeia posições das pulseiras para comandos do jogo com zonas circulares personalizadas e textos centralizados.
    """

    def __init__(self, frame_shape=(480, 640)):
        height, width = frame_shape[:2]
        self.last_blue_command = None
        self.last_red_command = None
        self.last_command_time = 0
        self.command_cooldown = 0.2
        radius = 55
        self.zones = {
            "W": {
                "pos": (int(width * 0.18), int(height * 0.11)),
                "radius": radius,
                "color": (255, 0, 0),
            },
            "A": {
                "pos": (int(width * 0.08), int(height * 0.50)),
                "radius": radius,
                "color": (255, 0, 0),
            },
            "S": {
                "pos": (int(width * 0.18), int(height * 0.89)),
                "radius": radius,
                "color": (255, 0, 0),
            },
            "D": {
                "pos": (int(width * 0.38), int(height * 0.50)),
                "radius": radius,
                "color": (255, 0, 0),
            },
            "X": {
                "pos": (int(width * 0.62), int(height * 0.50)),
                "radius": radius,
                "color": (0, 0, 255),
            },
            "Y": {
                "pos": (int(width * 0.82), int(height * 0.11)),
                "radius": radius,
                "color": (0, 0, 255),
            },
            "B": {
                "pos": (int(width * 0.82), int(height * 0.89)),
                "radius": radius,
                "color": (0, 0, 255),
            },
            "A_r": {
                "pos": (int(width * 0.92), int(height * 0.50)),
                "radius": radius,
                "color": (0, 0, 255),
            },
        }
        self.blue_commands = {"W", "A", "S", "D"}
        self.red_commands = {"X", "Y", "B", "A_r"}

    def get_zone(self, center):
        if center is None:
            return None
        x, y = center
        for key, zone in self.zones.items():
            zx, zy = zone["pos"]
            r = zone["radius"]
            if (x - zx) ** 2 + (y - zy) ** 2 <= r**2:
                return key
        return None

    def map_gesture(self, center, frame_shape, color):
        if center is None:
            return None

        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return None

        zone = self.get_zone(center)
        if zone is None:
            return None

        command = None
        if color == "blue" and zone in self.blue_commands:
            command = zone
            if command == self.last_blue_command:
                return None
            self.last_blue_command = command
        elif color == "red" and zone in self.red_commands:
            command = "A" if zone == "A_r" else zone
            if command == self.last_red_command:
                return None
            self.last_red_command = command

        if command:
            self.last_command_time = current_time
        return command

    def reset_commands(self):
        self.last_blue_command = None
        self.last_red_command = None

    def draw_zones(self, frame):
        result = frame.copy()
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 4
        for key, zone in self.zones.items():
            color = zone["color"]
            x, y = zone["pos"]
            r = zone["radius"]
            cv2.circle(result, (x, y), r, color, 3)
            txt = "A" if key == "A_r" else key
            ((tw, th), _) = cv2.getTextSize(txt, font, font_scale, thickness)
            tx = x - tw // 2
            ty = y + th // 2
            cv2.putText(
                result, txt, (tx, ty), font, font_scale, color, thickness, cv2.LINE_AA
            )
        cv2.line(result, (width // 2, 0), (width // 2, height), (50, 255, 100), 2)
        cv2.line(result, (0, height // 2), (width, height // 2), (50, 255, 100), 2)

        return result

    def get_command_description(self, command):
        descriptions = {
            "W": "Mover para Cima (Azul)",
            "S": "Mover para Baixo (Azul)",
            "A": "Mover para Esquerda (Azul/Vermelho)",
            "D": "Mover para Direita (Azul)",
            "X": "Ação 1 (Vermelho)",
            "Y": "Ação 2 (Vermelho)",
            "B": "Ação 3 (Vermelho)",
        }
        return descriptions.get(command, "Comando Desconhecido")
