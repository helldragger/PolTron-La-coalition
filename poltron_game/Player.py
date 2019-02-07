from poltron_game.TeamItems import *


"""
	author: Alexis Mortelier
"""


class Player(TeamItems):
    speed = 1

    def __init__(self, x, y, team):
        TeamItems.__init__(self, x, y, team)
        self.code = "*"
        self.lastMove = ""

    def __moveDown(self):
        return (self.coord[0] + self.speed, self.coord[1])

    def __moveUp(self):
        return (self.coord[0] - self.speed, self.coord[1])

    def __moveLeft(self):
        return (self.coord[0], self.coord[1] - self.speed)

    def __moveRight(self):
        return (self.coord[0], self.coord[1] + self.speed)

    def nextMove(self, direction):
        if self.lastMove.upper() != "L" and direction.upper() == "D":
            return self.__moveRight()
        elif self.lastMove.upper() != "D" and direction.upper() == "Q":
            return self.__moveLeft()
        elif self.lastMove.upper() != "S" and direction.upper() == "Z":
            return self.__moveUp()
        elif self.lastMove.upper() != "Z" and direction.upper() == "S":
            return self.__moveDown()
        else:
            return False


    def applyMove(self, direction):
        self.lastMove = direction
        self.coord = self.nextMove(direction)
