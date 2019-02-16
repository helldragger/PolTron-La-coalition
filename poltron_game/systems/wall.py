from typing import Tuple

from poltron_game.constants import WALLS
from poltron_game.systems.positional_system import PositionalSystem


class WallSystem(PositionalSystem):
    def __init__(self):
        super().__init__()

    def is_wall(self, pos: Tuple[int, int]) -> bool:
        return pos in self.pos_system.get_all_positions(WALLS)

    def count(self) -> int:
        return len(self.pos_system.get_all_positions(WALLS))

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.pos_system.register_position(WALLS, new_pos)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        self.pos_system.register_position(WALLS, pos)

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        self.pos_system.unregister_position(WALLS, new_pos)
