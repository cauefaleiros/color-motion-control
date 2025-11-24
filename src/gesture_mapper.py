# commit
import cv2


class GestureMapper:
    def map_gesture(self, center, frame_shape, color):
        """
        Mapeia a posição da pulseira para um comando.
        """
        if center is None:
            return None

        height, width = frame_shape[:2]
        x, y = center

        # Divide o frame em 3 zonas horizontais e 3 verticais
        zone_h = height // 3
        zone_w = width // 3

        if y < zone_h:  # Topo
            if color == "blue":
                return "W"
            if color == "red":
                return "X"
        elif y > 2 * zone_h:  # Baixo
            if color == "blue":
                return "S"
            if color == "red":
                return "Y"
        elif x < zone_w:  # Esquerda
            if color == "blue":
                return "A"
            if color == "red":
                return "B"
        elif x > 2 * zone_w:  # Direita
            if color == "blue":
                return "D"
            if color == "red":
                return "Z"

        # Centro ou não mapeado
        return None

    def get_command_description(self, command):
        """Retorna uma descrição legível para o comando."""
        descriptions = {
            "W": "Mover para Cima",
            "S": "Mover para Baixo",
            "A": "Mover para Esquerda",
            "D": "Mover para Direita",
            "X": "Ação 1 (Topo Vermelho)",
            "Y": "Ação 2 (Baixo Vermelho)",
            "B": "Ação 3 (Esquerda Vermelho)",
            "Z": "Ação 4 (Direita Vermelho)",
        }
        return descriptions.get(command, "Comando Desconhecido")

    def draw_zones(self, frame):
        """
        Desenha as zonas de controle no frame para visualização.
        """
        result = frame.copy()
        height, width = frame.shape[:2]

        zone_h = height // 3
        zone_w = width // 3

        # Desenha linhas horizontais
        cv2.line(result, (0, zone_h), (width, zone_h), (255, 255, 255), 1)
        cv2.line(result, (0, 2 * zone_h), (width, 2 * zone_h), (255, 255, 255), 1)

        # Desenha linhas verticais
        cv2.line(result, (zone_w, 0), (zone_w, height), (255, 255, 255), 1)
        cv2.line(result, (2 * zone_w, 0), (2 * zone_w, height), (255, 255, 255), 1)

        return result
