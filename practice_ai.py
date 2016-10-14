#this is an AI that allows you to test your own AI with it.
#Note that it was not written in order to provide you with a good example.
#The code is made clumsy intentionally, so copying it will give you
#no advantage in a tournament

pos = [2,4] #y first, then x
rotation = 0 #initial location

def get_move():
    self.get_position()
    self.get_rotation()
    for i in range (0,9):
        for j in range (0,9):
            #check if position (i, j) == "robot"
                robot_pos = [i,j]
                break
    if (rotation == 0 and (position[0]+1) < robot_pos[0]) or (rotation == 1 and (position[1]+1) < robot_pos[1]):
        return "move 1"
    elif (rotation == 2 and (position[0]-1) > robot_pos[0]) or (rotation == 3 and (position[1]-1) > robot_pos[1]):
        return "move -1"
    elif (rotation == 1 and robot_pos[0] > position[0]+1) or (rotation == 2 and robot_pos):
        return "rotate 1"
    elif ():
        return "rotate -1"
    elif (rotation == 0 and (position[0]+1) == robot_pos[0]) or (rotation == 1 and (position[1]+1) == robot_pos[1]) or (rotation == 2 and (position[0]-1) == robot_pos[0]) or (rotation == 3 and (position[1]-1) == robot_pos[1]):
        return "attack 0"
    else:
        return "rotate 1"

    
                
