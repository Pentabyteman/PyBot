pos = 0
rotation = 0


def get_move():
    global pos, rotation
    if rotation < 2:
        rotation += 1
        return "rotate 1"
    elif pos < 3:
        pos += 1
        return "move 1"
    return "attack 0"
