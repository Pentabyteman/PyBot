# AI for the first tournament.
# Lost all games but one.

import numpy as np
import theano
import scipy
from numpy import exp, array, random, dot

randfelder = np.array([[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
                       [0, 5], [0, 6], [0, 7], [0, 8], [1, 0],
                       [2, 0], [3, 0], [4, 0], [5, 0], [6, 0],
                       [7, 0], [8, 0], [8, 1], [8, 2], [8, 3],
                       [8, 4], [8, 5], [8, 6], [8, 7], [8, 8],
                       [7, 8], [6, 8], [5, 8], [4, 8], [3, 8],
                       [2, 8], [1, 8]])

OUTPUT_DICTIONARY = {0 : "move 1", 1 : "rotate 1", 2 : "move -1", 3 : "rotate -1"}
RELATIVEFIELD_DICTIONARY = {0 : [-1, 0], 1 : [0, 1], 2 : [1, 0], 3 : [0, -1]}
ROTATION_DICTIONARY = {0 : 0, 1 : 1, 2: 0, 3 : 1}
distance_array = []

def check_passable(start, board_death):
        if board_death[start[0]][start[1]] != 1:
                return True
        else:
                return False
        
def relative_field(pos1, pos2, i, j):
        new_pos = [pos1+i, pos2+j]
        return new_pos

#FUNKTIONIERT
def drehen(rot, direction): 
        #richtung -1 = links
        #richtung +1 = rechts
        rot_list = [0, 1, 2, 3, 0, 1, 2, 3]
        new_rot = rot_list[rot + direction]
        return new_rot

#FUNKTIONIERT
def abstand(start, ziel, board_death):
        if check_passable(start, board_death):
                if start[0] == ziel[0] or start[1] == ziel[1]: #wenn keine rotation noetig
                    abstand = abs(start[0]-ziel[0]) + abs(start[1]-ziel[1])
                else:
                    abstand = abs(start[0]-ziel[0]) + abs(start[1]-ziel[1]) + 1 #eine rotation noetig
        else:
                abstand = 1000
        return abstand

#FUNKTIONIERT / UNNOETIG
def zwei_d_abfrage(array_1, array_2, index_1):
        if array_1[index_1][0] is array_2[0] and array_1[index_1][1] is array_2[0]:
                return True

#FUNKTIONIERT
def bewegen(start, rot, ziel, board_death, board_team):
        distance = [1000, 1000, 1000, 1000]
        position_l = [0, 1, 2, 3, 0, 1, 2, 3] #Nicht sehr schoen!
        positions_liste = [(0 + rot), (1 + rot), (2 + rot), (3 + rot)]
        for i in range(0, 4):
            position_rot = position_l[positions_liste[i]]
            if position_rot == 3: #no moving backwards
                distance[i] = 1000
            else:
                    new_pos = relative_field(*start, *RELATIVEFIELD_DICTIONARY[position_rot])
                    distance[i] = abstand(new_pos, ziel, board_death) + ROTATION_DICTIONARY[position_rot]
        distance[3] = 3000
        index_min = np.argmin(distance)
        return OUTPUT_DICTIONARY[index_min], distance[index_min]

def find_next_point(start, goal):
        result_list = []
        for i in range(0, goal.shape[0]):
                if goal[i][0] == 1000:
                        result_list.append(1000)
                else:
                        delta_x = goal[i][0]-start[0]
                        delta_y = goal[i][1]-start[1]
                        #no need to worry about square roots, we only need relativ distance!
                        distance_squared = np.square(delta_x)+np.square(delta_y)
                        result_list.append(distance_squared)
        index_fastest = np.argmin(result_list)
        point = [goal[index_fastest][0], goal[index_fastest][1]]
        return point
                                
                
def neighbours(field):
        neighbour1 = [field[0]-1, field[1]]
        neighbour2 = [field[0]+1, field[1]]
        neighbour3 = [field[0], field[1]-1]
        neighbour4 = [field[0], field[1]+1]
        return neighbour1, neighbour2, neighbour3, neighbour4

def field_ahead(myRot, myPos):
        if myRot == 0:
            new_pos = [myPos[0]-1, myPos[1]]
        elif myRot == 1:
            new_pos = [myPos[0], myPos[1]+1]
        elif myRot == 2:
            new_pos = [myPos[0]+1, myPos[1]]
        else:
            new_pos = [myPos[0], myPos[1]-1]
        return new_pos

def field_behind(myRot, myPos):
        if myRot == 2:
            new_pos = [myPos[0]+1, myPos[1]]
        elif myRot == 3:
            new_pos = [myPos[0], myPos[1]-1]
        elif myRot == 0:
            new_pos = [myPos[0]-1, myPos[1]]
        else:
            new_pos = [myPos[0], myPos[1]+1]
        return new_pos

def find_next_goal(matrix, team_matrix, myRot, myPos, entity_pos, count, kind, old_target):
        possible_fields = np.array([[1000, 1000]])
        update = False
        for row in range (1, 8):
            for col in range (1, 8):
                    chosen_field = [row, col]
                    if chosen_field == myPos:
                            pass
                    if kind == 1:
                            chosen_field_value = matrix[row][col]
                    else:
                            chosen_field_value = team_matrix[row][col]
                    if chosen_field_value == 1:
                        pass
                    else:
                       if kind == 1:
                               neighbour1, neighbour2, neighbour3, neighbour4 = neighbours(chosen_field)
                               neighbour1_value = matrix[neighbour1[0]][neighbour1[1]]
                               neighbour2_value = matrix[neighbour2[0]][neighbour2[1]]
                               neighbour3_value = matrix[neighbour3[0]][neighbour3[1]]
                               neighbour4_value = matrix[neighbour4[0]][neighbour4[1]]
                               
                               if [neighbour1_value == 1, neighbour2_value == 1, neighbour3_value == 1, neighbour4_value == 1].count(True) > count:
                                   new_field = np.array([[row, col]])
                                   if possible_fields is not None:
                                        possible_fields = np.concatenate((possible_fields, new_field), axis=0)
                                   else:
                                        possible_fields = np.array(new_field)
                       else:
                                new_field = np.array([[row, col]])
                                if possible_fields is not None:
                                    possible_fields = np.concatenate((possible_fields, new_field), axis=0)
                                else:
                                    possible_fields = np.array(new_field)   
        if np.array_equal(possible_fields, [[1000, 1000]]):
                another_round = find_next_goal(matrix, team_matrix, myRot, myPos, entity_pos, count-1, kind, old_target)
                return another_round
        elif possible_fields is not None:
                next_move_array = []
                distances_array = []
                for i in range(0, possible_fields.shape[0]):
                        if possible_fields[i][0] == old_target[0] and possible_fields[i][1] == old_target[1]:
                                next_move, distance = "rotate 1", 2000
                        else:
                                next_move, distance = bewegen(myPos, myRot, possible_fields[i], matrix, team_matrix)
                        next_move_array.append(next_move)
                        distances_array.append(distance)
                        if possible_fields[i][0] == myPos[0] and possible_fields[i][1] == myPos[1]:
                                update = True
                if update == True:
                        old_target = myPos
                definitely_next_move = next_move_array[np.argmin(distances_array)]
                return definitely_next_move, old_target
        
def get_action(ask_for_field, turns_to_go, position=None, rotation=None):
    global pos, rot, my_team, board_dangerous, board_death, bord_team, old_target
    obstacle = None
    entity_pos = None
    team_array = None
    board_team = None
    
    if position is not None and rotation is not None:
        old_target = [-8. -1]
        pos = list(position)
        rot = rotation
        passable, my_team, entity = ask_for_field(position[0], position[1])
        
    for row in range(9):
        for col in range(9):
            passable, team, is_entity = ask_for_field(row, col)
            if team == my_team:
                new_value = np.array([[row, col]])
                if team_array is not None:
                        team_array = np.concatenate((team_array, new_value), axis=0)
                else:
                        team_array = np.array(new_value)
            if is_entity and team == my_team:
                pos = [row, col]
            elif is_entity:
                entity_pos = [row, col]
            else:
                if passable is False:
                    new_value = np.array([[row, col]])
                    if obstacle is not None:
                        obstacle = np.concatenate((obstacle, new_value), axis=0)
                    else:
                        obstacle = np.array(new_value)
    #initializing
    if turns_to_go >= 35:          
        board_death = np.zeros((9, 9))
        for i in range(0, obstacle.shape[0]):
            board_death[obstacle[i][0], obstacle[i][1]] = 1
        board_dangerous = scipy.ndimage.binary_dilation(board_death).astype(int)
        for i in range(0, randfelder.shape[0]):
            board_dangerous[randfelder[i][0], randfelder[i][1]] = 1
        next_goal, old_target = find_next_goal(board_dangerous, board_team, rot, pos, entity_pos, 4, 1, old_target)
        
    if turns_to_go < 35:
        board_team = np.zeros((9, 9))
        for i in range(0, team_array.shape[0]):
            board_team[team_array[i][0], team_array[i][1]] = 1
        next_goal, old_target = find_next_goal(board_dangerous, board_team, rot, pos, entity_pos, 4, 2, old_target)
            
    #main part
    alpha = field_ahead(rot, pos)
    beta = field_ahead(rot, entity_pos)
    gamma = field_behind(rot, pos)
    try:
            if alpha[0] == entity_pos[0] and alpha[1] == entity_pos[1]:
                if board_death[beta[0]][beta[1]] == 1 or board_death[gamma[0]][gamma[1]] == 1:
                    return "attack 1"
                else:
                    return "attack 0"
            elif gamma[0] == entity_pos[0] and gamma[1] == entity_pos[1]:
                if board_death[alpha[0]][alpha[1]] != 1:
                        return "move 1"
                else:
                        pass
    except:
            pass
    cmd, arg = next_goal.split(" ")
    if cmd == "rotate":
            rot = drehen(rot, int(arg))
    return next_goal
