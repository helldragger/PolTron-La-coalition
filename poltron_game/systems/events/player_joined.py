from typing import Tuple

from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class PlayerJoinedEvent(Event):

    def __init__(self, player: int, team: int, pos: Tuple[int, int]):
        self.player = player
        self.team = team
        self.pos = pos

    def process_func(self, system: Updatable):
        system.on_player_joined(self.player, self.team, self.pos)
