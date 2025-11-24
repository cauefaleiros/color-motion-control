import logging

from pynput.keyboard import Controller

keyboard = Controller()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

COMMAND_MAP = {
    "W": "w",
    "A": "a",
    "S": "s",
    "D": "d",
    "X": "x",
    "Y": "y",
    "B": "b",
    "Z": "z",
}


def press_command(command):
    if command is None or command not in COMMAND_MAP:
        return
    key = COMMAND_MAP[command]
    try:
        keyboard.press(key)
        keyboard.release(key)
        logging.info(f"Tecla pressionada: {key}")
    except Exception as e:
        logging.error(f"Erro ao pressionar tecla {key}: {e}")
