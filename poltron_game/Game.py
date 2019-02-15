import random
import paranoid
"""
	author: Alexis Mortelier
        contributor: Vincent DE MENEZES
"""
class Game(object):

    def __init__(self, row, col, nbCoa):
        self.row = row
        self.col = col
        self.nbCoa = nbCoa
        self.board = {"players" : {"attacker" : [], "defender" : []} , "wall" : []}
        self.importantMoment = []
        self.tour = 0

    def __displayBoard(self):
        res = ""
        for row in range(self.row):
            for col in range(self.col):
                coord = (row,col)
                if coord in self.board["players"]["attacker"]:
                    res += "*"
                elif coord in self.board["players"]["defender"]:
                    res += "%"
                elif coord in self.board["wall"]:
                    res += "#"
                else:
                    res += "O"
                res += " "
            res += "\n"
        return res

    def __initGame(self):
        row = random.sample(range(0, self.row), self.nbCoa+1)
        col = random.sample(range(0, self.col), self.nbCoa+1)
        
        self.board["players"]["attacker"].append((row[0], col[0]))
        for i in range(1, len(row)):
            self.board["players"]["defender"].append((row[i], col[i]))      
        
    def copy(self):
        newG = Game(self.row, self.col, self.nbCoa)
        newG.board = {"players" : { "attacker" : self.board["players"]["attacker"].copy(), "defender" : self.board["players"]["defender"].copy()}, "wall" : self.board["wall"].copy()}
        return newG
    
    def endGame(self):
        if len(self.board["players"]["attacker"]) != 0 and len(self.board["players"]["defender"]) != 0:
                return False
        return True

    def isDying(self, nextMove):
        if nextMove[0] < 0 or nextMove[1] < 0 or nextMove[0] > self.row-1 or nextMove[1] > self.col-1:
            return True
        if nextMove in self.board["players"]["attacker"] or nextMove in self.board["players"]["defender"]:
            return True
        if nextMove in self.board["wall"]:
            return True
        return False

    def __saveImportantMoment(self):
        self.importantMoment.append([self.row, self.col, self.nbCoa, len(self.board["players"]["defender"]), len(self.board["wall"][1:])])

    def nextMove(self, coord, direction):
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
    def getAttacker(self):
        return self.board["players"]["attacker"]

    def getDefender(self):
        return self.board["players"]["defender"]

    def getWall(self):
        return self.board["wall"]

    def testGame(self):
        self.__initGame()
        while not self.endGame():
            for team, players in self.board["players"].items():
                for p in players:
                    ##test exec
                    print(self.__displayBoard())
                    print("Wall : ", self.board["wall"])
                    print("Attaquant : ", self.board["players"]["attacker"])
                    print("Defenseur : ", self.board["players"]["defender"])
                    print("TEAM : ", team, "JOUEUR : ", self.board["players"][team].index(p) + 1)
                    mov = input("direction : ")
                    nextMove = self.__nextMove(p,mov)
                    print (nextMove)
                    if nextMove != False:
                        indexP = self.board["players"][team].index(p)
                        self.board["wall"].append(p)
                        print("is Dying ? : ", self.isDying(nextMove))
                        if self.isDying(nextMove):
                            self.__saveImportantMoment()
                            self.board["players"][team].remove(self.board["players"][team][indexP])
                        else:
                            self.board["players"][team][indexP] = nextMove
                        self.tour += 1
                    print("Important Moment : ", self.importantMoment)

    def testIA(self, depthAttacker, depthDefender):
        self.__initGame()
        teamDepth = {"attacker" : depthAttacker, "defender" : depthDefender}
        while not self.endGame():
            for team, players in self.board["players"].items():
                for p in players:
                    print(self.__displayBoard())
                    indexP = self.board["players"][team].index(p)
                    mov = paranoid.algorithmParanoid(self, teamDepth.get(team), team, p, indexP)
                    print("Team : ", team, " Joueur : ", indexP, " Move : ",mov)
                    nextMove = self.nextMove(p,mov)
                    if nextMove != False:
                        self.board["wall"].append(p)
                        if self.isDying(nextMove):
                            self.__saveImportantMoment()
                            self.board["players"][team].remove(self.board["players"][team][indexP])
                            if self.endGame():
                                break
                        else:
                            self.board["players"][team][indexP] = nextMove
                        self.tour += 1
        print(self.__displayBoard())

if __name__ == "__main__":
    g = Game(8, 8, 2)
    g.testIA(8, 4)
