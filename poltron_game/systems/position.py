from typing import Dict, Set, Tuple

from poltron_game.constants import COALITION, SOLO, WALLS


class PositionSystem:

    def __init__(self):
        self.type_to_pos: Dict[int, Set[Tuple[int, int]]] = {
            SOLO:      set(),
            COALITION: set(),
            WALLS:     set()
        }

        self.pos_to_type: Dict[Tuple[int, int], int] = {
        }
        # unique pairs of values
        self.key_to_pos: Dict[int, Tuple[int, int]] = {
        }

    def register_position(self, key: int, pos: Tuple[int, int]):
        assert key in self.type_to_pos.keys()
        assert pos not in self.type_to_pos[key]
        self.type_to_pos[key].add(pos)
        assert pos not in self.pos_to_type.keys()
        self.pos_to_type[pos] = key

    def register_unique_position(self, key: int, pos: Tuple[int, int]):
        assert key not in self.key_to_pos.keys()
        self.key_to_pos[key] = pos
        assert pos not in self.pos_to_type.keys()
        self.pos_to_type[pos] = key

    def unregister_position(self, key: int, pos: Tuple[int, int]):
        assert key in self.type_to_pos.keys()
        assert pos in self.type_to_pos[key]
        self.type_to_pos[key].remove(pos)
        assert pos in self.pos_to_type.keys()
        del self.pos_to_type[pos]

    def unregister_unique_position(self, key: int, pos: Tuple[int, int]):
        assert key in self.key_to_pos.keys()
        del self.key_to_pos[key]
        assert pos in self.pos_to_type.keys()
        del self.pos_to_type[pos]

    def get_all_positions(self, key: int) -> Set[Tuple[int, int]]:
        assert key in self.type_to_pos.keys()
        return self.type_to_pos[key]

    def get_unique_position(self, key: int) -> Tuple[int, int]:
        assert key in self.key_to_pos.keys()
        return self.key_to_pos[key]

    def get_position_type(self, pos: Tuple[int, int]) -> int:
        assert pos in self.pos_to_type.keys()
        return self.pos_to_type[pos]

    def get_all_types_to_positions_items(self):
        return self.type_to_pos.items()
