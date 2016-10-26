#Written by Pentabyteman
#This is for demonstration and training purposes only. DON'T RELY ON THIS FOR THE TOURNAMENT
#Most of the code is written "grauselig" on purpose 

def get_move(ask_for_field, turns_to_go, position=None, rotation=None):
global pos, rot, rows_to_go, cols_to_go
if position is not None and rotation is not None:
        pos = list(position)
        rot = rotation
        passable, my_team, entity = ask_for_field(position)
if rot == 0:
