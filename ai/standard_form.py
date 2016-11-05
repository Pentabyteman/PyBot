#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

# This is the standard form your ai programm should follow
# The spaces are left intentionally


def get_action(ask_for_field, turns_to_go, position=None, rotation=None):
    # Watch out: You are only given the rotation and position at the first
    # move. Every move after thay, you will have to calculate it yourself

    # passable, team, is_entity = ask_for_field(row, col)
    # calculate best movements here

    # Attention:
    # If you move into a wall or outside of the board, you loose
    # automatically, so be sure to double-check this!

    # "move 1" means move forward
    # "move -1" means move backwards
    # "rotate 1" is a rotation to the right
    # "rotate(-1" is a rotation to the left

    # Attention:
    # If you try to attack a field where no robot stands, you loose
    # automatically, so be sure to double-check this!

    # "attack 0"
    # "attack 1"

    return  # return movetype
