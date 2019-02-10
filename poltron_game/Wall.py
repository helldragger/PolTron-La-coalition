from poltron_game.TeamItems import *


"""
	author: Alexis Mortelier
"""


class Wall(TeamItems):

    def __init__(self, x, y, team):
        TeamItems.__init__(self, x, y, team)
        self.code = "#"
