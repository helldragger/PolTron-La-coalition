from typing import Tuple

from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class PlayerKillEvent(Event):

    def __init__(self, player: int, last_pos: Tuple[int, int]):
        self.player = player
        self.last_pos = last_pos

    def process_func(self, system: Updatable):
        system.on_player_kill(self.player, self.last_pos)
