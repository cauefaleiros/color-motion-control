from pynput.keyboard import Controller, Key
keyboard = Controller()

COMMAND_MAP = {
    'W': 'w',
    'A': 'a',
    'S': 's',
    'D': 'd',
    'X': 'x',
    'Y': 'y',
    'B': 'b',
    'Z': 'z'
}

def press_command(command):
    if command is None or command not in COMMAND_MAP:
        return
    key = COMMAND_MAP[command]
    try:
        keyboard.press(key)
        keyboard.release(key)
    except Exception as e:
        print(f"Erro ao pressionar tecla {key}: {e}")
