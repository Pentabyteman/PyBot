pos, rot, rows_to_go, cols_to_go = 0, 0, 0, 0


def get_move(ask_for_field, turns_to_go, position=None, rotation=None):
    global pos, rot, rows_to_go, cols_to_go
    if position is not None and rotation is not None:
        pos = list(position)
        rot = rotation

        for row in range(9):
            for col in range(9):
                passable, team, is_entity = ask_for_field(row, col)
                if is_entity:
                    entity_pos = (row, col)
                    break

        rows_to_go, cols_to_go = [e - s for s, e in zip(pos, entity_pos)]
        print("rows to go", rows_to_go)
        rows_to_go = rows_to_go + 1 if rows_to_go < 0 else rows_to_go - 1
        cols_to_go = cols_to_go + 1 if cols_to_go < 0 else cols_to_go - 1
        print("rows to go", rows_to_go)

    # ACHTUNG GRAUSELIG! NICHT NACHMACHEN!
    if rows_to_go != 0:
        if rows_to_go > 0 and rot != 2:
            rot_diff = min(1, max(-1, 2 - rot))
            rot += rot_diff
            return "rotate {0}".format(rot_diff)
        elif rows_to_go < 0 and rot != 0:
            rot_diff = min(1, max(-1, 0 - rot))
            rot += rot_diff
            return "rotate {0}".format(rot_diff)
        else:
            row_diff = min(1, max(-1, rows_to_go))
            pos[0] += row_diff
            rows_to_go = rows_to_go - 1 if rows_to_go > 0 else rows_to_go + 1
            return "move {0}".format(row_diff)

    return "attack 1"
