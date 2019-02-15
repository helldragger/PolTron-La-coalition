from poltron_game.systems.position import PositionSystem
from poltron_game.systems.updatable import Updatable


class PositionalSystem(Updatable):
    def __init__(self):
        self.pos_system = PositionSystem()
