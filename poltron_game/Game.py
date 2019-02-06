import random
"""
	author: Alexis Mortelier
"""
class Game(object):

    def __init__(self, row, col, nbCoa):
        self.row = row
        self.col = col
        self.nbCoa = nbCoa
        self.board = {"players" : {"attaquant" : [], "defenseur" : []} , "wall" : []}
        self.importantMoment = []
        self.tour = 0

    def __displayBoard(self):
        res = ""
        for row in range(self.row):
            for col in range(self.col):
                coord = (row,col)
                if coord in self.board["players"]["attaquant"]:
                    res += "A"
                elif coord in self.board["players"]["defenseur"]:
                    res += "D"
                elif coord in self.board["wall"]:
                    res += "#"
                else:
                    res += "O"
                res += " "
            res += "\n"
        return res

    def __generatePlayers(self):
        row = random.sample(range(0, self.row), self.nbCoa+1)
        col = random.sample(range(0, self.col), self.nbCoa+1)
        
        self.board["players"]["attaquant"].append((row[0], col[0]))
        for i in range(1, len(row)):
            self.board["players"]["defenseur"].append((row[i], col[i]))

    def __initGame(self):
        self.__generatePlayers()        
        
    def __endGame(self):
        if len(self.board["players"]["attaquant"]) != 0 and len(self.board["players"]["defenseur"]) != 0:
                return False
        return True

    def __isDying(self, nextMove):
        if nextMove[0] < 0 or nextMove[1] < 0 or nextMove[0] > self.row-1 or nextMove[1] > self.col-1:
            return True
        if nextMove in self.board["players"]["attaquant"] or nextMove in self.board["players"]["defenseur"]:
            return True
        if nextMove in self.board["wall"]:
            return True
        return False

    def __saveImportantMoment(self):
        self.importantMoment.append([self.row, self.col, self.nbCoa, len(self.board["players"]["defenseur"]), len(self.board["wall"][1:])])

    def __nextMove(self, coord, direction):
        if direction.upper() == "D":
            return (coord[0], coord[1] + 1)
        elif direction.upper() == "Q":
            return (coord[0], coord[1] - 1)
        elif direction.upper() == "Z":
            return (coord[0] - 1, coord[1])
        elif direction.upper() == "S":
            return (coord[0] + 1, coord[1])
        else:
            return False


    def testGame(self):
        self.__initGame()
        while not self.__endGame():
            for team, players in self.board["players"].items():
                for p in players:
                    ##test exec
                    print(self.__displayBoard())
                    print("Wall : ", self.board["wall"])
                    print("Attaquant : ", self.board["players"]["attaquant"])
                    print("Defenseur : ", self.board["players"]["defenseur"])
                    mov = input("direction : ")
                    nextMove = self.__nextMove(p,mov)
                    print (nextMove)
                    if nextMove != False:
                        indexP = self.board["players"][team].index(p)
                        self.board["wall"].append(p)
                        print("is Dying ? : ", self.__isDying(nextMove))
                        if self.__isDying(nextMove):
                            self.__saveImportantMoment()
                            self.board["players"][team].remove(self.board["players"][team][indexP])
                        else:
                            self.board["players"][team][indexP] = nextMove
                        self.tour += 1
                    print("Important Moment : ", self.importantMoment)


if __name__ == "__main__":
    g = Game(5, 5, 2)
    g.testGame()
