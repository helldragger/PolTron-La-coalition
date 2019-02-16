from typing import Tuple

from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class PlayerRollbackEvent(Event):

    def __init__(self, player: int, old_pos: Tuple[int, int],
                 new_pos: Tuple[int, int]):
        self.player = player
        self.old_pos = old_pos
        self.new_pos = new_pos

    def process_func(self, system: Updatable):
        system.on_player_rollback(self.player, self.old_pos, self.new_pos)
