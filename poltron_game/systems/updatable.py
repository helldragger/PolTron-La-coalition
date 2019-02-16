from typing import Tuple


class Updatable:

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        pass

    def on_player_kill(self, player: int, last_pos: Tuple[int, int]):
        pass

    def on_player_revival(self, player: int, last_pos: Tuple[int, int]):
        pass

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        pass

    def on_turn_ended(self):
        pass

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        pass

    def on_player_turn_ended(self):
        pass

    def on_turn_rollback(self):
        pass

    def on_player_turn_rollback(self):
        pass

    def on_game_ended(self):
        pass
