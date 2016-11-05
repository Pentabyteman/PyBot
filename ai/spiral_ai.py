#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# Written by Pentabyteman
# This is for demonstration and training purposes only.
# DON'T RELY ON THIS FOR THE TOURNAMENT
# Most of the code is written "grauselig" on purpose


def get_move(ask_for_field, turns_to_go, position=None, rotation=None):
    global pos, rot, my_team
    if position is not None and rotation is not None:
        pos = list(position)
        rot = rotation
        passable, my_team, entity = ask_for_field(position[0], position[1])

    for i in range(0, 9):  # end is exclusive
        for j in range(0, 9):
            passable, team, is_entity = ask_for_field(i, j)
            if is_entity and team == my_team:
                pos = [i, j]
                break
    if rot == 0:
        field_ahead = [pos[0] - 1, pos[1]]
    elif rot == 1:
        field_ahead = [pos[0], pos[1] + 1]
    elif rot == 2:
        field_ahead = [pos[0] + 1, pos[1]]
    else:
        field_ahead = [pos[0], pos[1] - 1]

    if field_ahead[0] < 0 or field_ahead[
            0] > 8 or field_ahead[1] < 0 or field_ahead[1] > 8:
        passable = False
        is_entity = False
    else:
        passable, team, is_entity = ask_for_field(
            field_ahead[0], field_ahead[1])

    if is_entity:
        return "attack 1"
    elif passable is False or team == my_team:
        rot += 1
        if rot > 3:
            rot = 0
        return "rotate 1"
    else:
        return "move 1"
