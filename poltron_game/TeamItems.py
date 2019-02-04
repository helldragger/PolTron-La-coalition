"""
	author: Alexis Mortelier
"""


class TeamItems(object):

    def __init__(self, x, y, team):
        self.coord = (x, y)
        self.team = team
        self.code = ""

    def getX(self):
        return self.coord[0]

    def getY(self):
        return self.coord[1]

    def getCoord(self):
        return self.coord

    def getTeam(self):
        return self.team

    def getCode(self):
        return self.code
