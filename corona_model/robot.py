#******************************************************************************
# robot.py
#******************************************************************************
# Name: Kukai nakahata
#******************************************************************************
# Collaborators/outside sources used 
#(IMPORTANT! Write "NONE" if none were used):
#
#NONE
#
# Reminder: you are to write your own code.
#******************************************************************************
# Overall notes (not to replace inline comments):
#
#
import random
class Robogame():
    def __init__(self): #initialize the robot and prize
        self._robot = [random.randint(0,5), random.randint(0,5)]
        self._prize = [random.randint(0,5), random.randint(0,5)]
    
    def challenge(self): # initialize extra variables needed for the challenge qustion
        self.robot_position = [self._robot] # this array keeps all [x,y] of the robot because he cant go back
        self._win1 = False
        self._win2 = False
        self._prize2 = [random.randint(0,5), random.randint(0,5)]

    def challenge_step(self): # this takes a random step, ut will check if the robot landed on a coordinate which it was on previously
        while True:
            x,y = self._robot
            if [x+1,y] in self.robot_position and [x-1,y] in self.robot_position and [x,y+1] in self.robot_position and [x,y-1] in self.robot_position:
                return False # return false if all foursides are locked
            direction = random.randint(0,4)# get a random value and 0~3 represents whih direction he will move to
            if direction == 0: x+=1
            elif direction == 1: x-=1
            elif direction == 2: y+=1
            else: y-=1 
            if [x,y] not in self.robot_position: # if the move is valid, then it will be added to the list of previous position and take the move
                self.robot_position.append([x,y])
                self._robot = [x,y]
                return True

    def set_prize(self,x,y):
        self._prize = [x,y]
    def set_prize2(self,x,y):
        self._prize2 = [x,y]
    def set_robot(self,x,y):
        self._robot = [x,y]

    def display(self, challenge = False): # this will display the position of the robot and the prizes, for the challenge "*" is used to show where the robot have been
        for i in range(6):
            for j in range(6):
                if self._robot == [i,j] and (self._robot == self._prize or self._robot == self._prize2):
                    print("C", end = "")
                elif self._robot == [i,j]:
                    print("R", end = "")
                elif challenge == True and self._robot == [i,j] and self._robot == self._prize2:
                    print("C2", end = "")
                elif challenge == True and self._prize2 == [i,j]:
                    print("P2", end = "")
                elif self._prize == [i,j]:
                    print("P", end = "")
                else:
                    if challenge == True and [i,j] in self.robot_position:
                        print("*", end="")
                    else:
                        print(".", end = "")
            print("")
        print("___________________________________")

    def win(self): # checks conditions for winning
        if self._prize == self._robot:
            return True
        return False

    def challenge_win(self): #checks conditions for winning
        if self._prize == self._robot: self._win1 = True
        if self._prize2 == self._robot: self._win2 = True
        if self._win1 == True and self._win2 == True: return True
        return False

    def off_grid(self): # checks if the robot is off the grid
        x, y = self._robot
        if x > 5 or x < 0 or y > 5 or y < 0:
            return True
        return False  
    
    def step(self): # the robot takes a random walk
        x,y = self._robot
        direction = random.randint(0,4)
        if direction == 0: x+=1
        elif direction == 1: x-=1
        elif direction == 2: y+=1
        else: y-=1 
        self._robot = [x,y]
    
simulation = 10000
num_win = 0
for i in range(simulation):
    game = Robogame()# starts game
    while True:# loop until robot wins or is off grid
        if game.win():
            num_win +=1
            break
        if game.off_grid():
            break
        game.step()
print("{0}% of the games were won by robot".format(100*num_win/simulation))# print the fraction of the games the robot won

###########################challenge##########################
simulation = 100000
num_win = 0
print("challenge")
for i in range(simulation):# loops the game and for each instance, initialize the challenge mode
    game = Robogame()
    game.challenge()
    while True:# a single game ends when the robot gets both prizes or is out of grid
        #game.display(True)
        if game.challenge_win():
            num_win +=1
            break
        if game.off_grid():
            break
        if game.challenge_step() == False:# true represents when there are valid moves and false if the robot cannot move anymore
            break
print("{0}% of the games were won in challenge".format(100*num_win/simulation))
