from typing import Tuple

from poltron_game.Game import Game
from poltron_game.systems.updatable import Updatable


class LogSystem(Updatable):
    def __init__(self, game: Game, print_screen=False):
        self.importantMoment: list = []
        self.game = game
        self.print_screen = print_screen


    def on_player_kill(self, player: int, last_pos: Tuple[int, int]):
        from poltron_game.constants import COALITION
        self.importantMoment.append([self.game.m, self.game.n, self.game.c,
                                     self.game.team_system.get_team_count(
                                         COALITION),
                                     self.game.wall_system.count()])

    def on_turn_ended(self):
        if self.print_screen:
            print(self.game._generate_board_string())

    def on_turn_rollback(self):
        self.game.tick -= 1
