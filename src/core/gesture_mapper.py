def map_gesture(center, frame_shape, color):

    if center is None:
        return None

    height, width = frame_shape[:2]
    x, y = center

    if y < height // 3:
        if color == 'blue':
            return 'W'
        if color == 'red':
            return 'X'
    elif y > (2 * height) // 3:
        if color == 'blue':
            return 'S'
        if color == 'red':
            return 'Y'
    elif x < width // 3:
        if color == 'blue':
            return 'A'
        if color == 'red':
            return 'B'
    elif x > (2 * width) // 3:
        if color == 'blue':
            return 'D'
        if color == 'red':
            return 'Z'

    return None
