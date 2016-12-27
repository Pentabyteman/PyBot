#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

# erste KI für PyBot, 9.-13. November 2016

import random

pos, rot = 0, 0
move = "move 1"

def get_action(ask_for_field, turns_to_go, position=None, rotation=None):
    global pos, rot, move, own_team
    if position is not None and rotation is not None:
        pos = list(position)
        rot = rotation
        own_team = ask_for_field(*pos)[1]

    def update_pos(pos, move):
        for row in range(9):
            for col in range(9):
                passable, team, is_entity = ask_for_field(row, col)
                if is_entity and team == own_team:
                    pos = (row, col)
                    break
        return pos

    def update_rot(rot, move):
        if move == "rotate 1":
            rot += 1
        elif move == "rotate -1":
            rot -= 1
        if rot > 3:
            rot -= 4
        elif rot < 0:
            rot += 4
        return rot

    def calculate_move(pos, rot):
        if not pos[0] == 0:
            if not pos[0] == 8:
                if not pos[1] == 0:
                    if not pos[1] == 8:
                        if rot == 0:
                            passable, team, is_entity = ask_for_field(pos[0]-1, pos[1])
                            if is_entity and team != own_team:
                                move = "attack 0"
                            else:
                                move = "move 1"
                        elif rot == 2:
                            passable, team, is_entity = ask_for_field(pos[0]+1, pos[1])
                            if is_entity and team != own_team:
                                move = "attack 0"
                            else:
                                move = "move 1"
                        elif rot == 1:
                            passable, team, is_entity = ask_for_field(pos[0], pos[1]+1)
                            if is_entity and team != own_team:
                                move = "attack 0"
                            else:
                                move = "move 1"
                        elif rot == 3:
                            passable, team, is_entity = ask_for_field(pos[0], pos[1]-1)
                            if is_entity and team != own_team:
                                move = "attack 0"
                            else:
                                move = "move 1"
                    else:
                        if not rot == 1:
                            passable, team, is_entity = ask_for_field(pos[0]+1, pos[1])
                            if is_entity and team != own_team:
                                move = "attack 0"
                            else:
                                move = "move 1"
                else:
                    if not rot == 3:
                        passable, team, is_entity = ask_for_field(pos[0]-1, pos[1])
                        if is_entity and team != own_team:
                            move = "attack 0"
                        else:
                            move = "move 1"
            else:
                if not rot == 2:
                    passable, team, is_entity = ask_for_field(pos[0], pos[1]-1)
                    if is_entity and team != own_team:
                        move = "attack 0"
                    else:
                        move = "move 1"
        else:
            if not rot == 0:
                passable, team, is_entity = ask_for_field(pos[0], pos[1]+1)
                if is_entity and team != own_team:
                    move = "attack 0"
                else:
                    move = "move 1"


        abdrehpos = random.choice([4,5,6])
        abdrehpos2 = random.choice([1,2,3,4])
        if pos[0] < abdrehpos2:
            if rot == 0:
                move = "rotate 1"
        if pos[0] > abdrehpos:
            if rot == 2:
                move = "rotate 1"
        if pos[1] < abdrehpos2:
            if rot == 3:
                move = "rotate 1"
        if pos[1] > abdrehpos:
            if rot == 1:
                move = "rotate 1"

        if not move == "attack 0":
            if not move == "attack 1":
                if not pos[0] == 0:
                    if not pos[0] == 8:
                        if not pos[1] == 0:
                            if not pos[1] == 8:
                                if rot == 0:
                                    passable, team, is_entity = ask_for_field(pos[0]-1, pos[1])
                                    if not passable:
                                        move = "rotate 1"
                                elif rot == 2:
                                    passable, team, is_entity = ask_for_field(pos[0]+1, pos[1])
                                    if not passable:
                                        move = "rotate 1"
                                elif rot == 1:
                                    passable, team, is_entity = ask_for_field(pos[0], pos[1]+1)
                                    if not passable:
                                        move = "rotate 1"
                                elif rot == 3:
                                    passable, team, is_entity = ask_for_field(pos[0], pos[1]-1)
                                    if not passable:
                                        move = "rotate 1"


        return move

    pos = update_pos(pos, move)
    rot = update_rot(rot, move)
    move = calculate_move(pos, rot)

    return move

