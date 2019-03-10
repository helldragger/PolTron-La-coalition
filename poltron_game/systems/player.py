from typing import Tuple

from poltron_game.systems.positional_system import PositionalSystem


class PlayerSystem(PositionalSystem):

    def __init__(self):
        super().__init__()

    def get_solo_player_position(self) -> Tuple[int, int]:
        return self.get_player_position(0)

    def get_player_position(self, player: int) -> Tuple[int, int]:
        return self.pos_system.get_unique_position(player)

    def set_player_position(self, player: int, pos: Tuple[int, int]):
        self.pos_system.register_unique_position(player, pos)

    def remove_player_position(self, player: int):
        old_pos = self.get_player_position(player)
        self.pos_system.unregister_unique_position(player, old_pos)

    def move_player(self, player: int, pos: Tuple[int, int]):
        self.remove_player_position(player)
        self.set_player_position(player, pos)

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.move_player(player, new_pos)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        self.set_player_position(player, pos)

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        self.move_player(player, old_pos)
