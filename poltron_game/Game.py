import random

from poltron_game.Player import *
from poltron_game.Wall import *


"""
	author: Alexis Mortelier
"""


class Game(object):

    def __init__(self, row, col, nbCoa):
        self.row = row
        self.col = col
        self.nbCoa = nbCoa
        self.wall = []
        self.players = []
        self.importantMoment = []

    def __displayBoard(self):
        res = ""
        pCoord = []
        wCoord = []
        for p in self.players:
            pCoord.append(p.getCoord())
        for w in self.wall:
            wCoord.append(w.getCoord())

        for row in range(self.row):
            for col in range(self.col):
                if (row, col) in wCoord:
                    res += self.wall[0].getCode()
                elif (row, col) in pCoord:
                    res += self.players[pCoord.index((row, col))].getTeam()
                else:
                    res += "."
                res += " "
            res += "\n"
        return res

    def __generatePlayers(self):
        row = random.sample(range(0, self.row), self.nbCoa + 1)
        col = random.sample(range(0, self.col), self.nbCoa + 1)

        self.players.append(Player(row[0], col[0], "b"))
        print(row[0], col[0])
        for i in range(1, len(row)):
            print((row[i], col[i]))
            self.players.append(Player(row[i], col[i], "r"))

    def __initGame(self):
        self.tour = 0
        self.__generatePlayers()

    def __endGame(self):
        etat = self.players[0].getTeam()
        for p in self.players:
            if etat != p.getTeam():
                return False
        return True

    def __isDying(self, player, nextMove):
        if nextMove[0] < 0 or nextMove[1] < 0 or nextMove[0] > self.row - 1 or \
                nextMove[1] > self.col - 1:
            return True
        for p in self.players:
            if p != player and p.getCoord() == nextMove:
                return True
        for w in self.wall:
            if w.getCoord() == nextMove:
                return True
        return False

    def __saveImportantMoment(self):
        self.importantMoment.append(
            [self.row, self.col, self.nbCoa, len(self.players), len(self.wall)])

    def testGame(self):
        self.__initGame()
        while not self.__endGame():
            for p in self.players:
                ##test exec
                # print(self.__displayBoard())
                mov = p.nextMoveRandom()
                nextMove = p.nextMove(mov)
                # print (nextMove)
                if nextMove != False:
                    # print("is Dying ? : ", self.__isDying(p, nextMove))
                    self.wall.append(Wall(p.getX(), p.getY(), p.getTeam()))
                    ##Player dying by this move
                    if self.__isDying(p, nextMove):
                        self.__saveImportantMoment()
                        self.players.remove(p)
                    ##Player move in the indicate direction
                    else:
                        p.applyMove(mov)
                    self.tour += 1  # print("Wall : ", self.wall)  # print("Players : ", self.players)  # print("Important Moment : ", self.importantMoment)  ##next turn


    def iaGame(self):
        print("a completer une fois IA fait")
        pass


if __name__ == "__main__":
    g = Game(5, 5, 2)
    g.testGame()
