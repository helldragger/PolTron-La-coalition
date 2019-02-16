from typing import List, Tuple

from poltron_game.systems.updatable import Updatable


class OrderSystem(Updatable):
    def __init__(self, ds: int, dc: int):
        self.cursor: int = 0
        buffer_size: int = ds + dc
        self.order_lists: List[List[int]] = [[] for x in
                                             range(2 * buffer_size + 1)]
        self.buffer_amount: int = 2 * buffer_size + 1
        self.current_order_index: int = buffer_size


    def shift_previous(self, other: int):
        if other > 1:
            return self.shift_previous(other - 1)
        for i in range(self.buffer_amount - 1):
            index: int = self.buffer_amount - i - 1
            self.order_lists[index] = self.order_lists[index - 1].copy()
        self.cursor = max(len(self.current_order()) - 1, 0)
        return self


    def shift_next(self, other: int):
        if other > 1:
            return self.shift_next(other - 1)
        for i in range(self.buffer_amount - 1):
            index: int = i
            self.order_lists[index] = self.order_lists[index + 1].copy()
        self.cursor = 0
        return self

    def current_order(self) -> List[int]:
        return self.order_lists[self.current_order_index]

    def next_order(self) -> List[int]:
        return self.order_lists[self.current_order_index + 1]

    def next_player(self) -> int:
        self.cursor += 1
        if self.cursor >= len(self.current_order()):
            self.shift_next(1)
        return self.current_order()[self.cursor]

    def previous_player(self) -> int:
        self.cursor -= 1
        if self.cursor <= -1:
            self.shift_previous(1)
        return self.current_order()[self.cursor]

    def current_player(self) -> int:
        return self.current_order()[self.cursor]

    def append_player(self, player):
        self.next_order().append(player)

    def remove_last_appended_player(self):
        self.next_order().pop(len(self.next_order()) - 1)

    def remove_appended_player(self, player: int):
        self.next_order().remove(player)

    def is_new_rotation(self) -> bool:
        return self.cursor == 0

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.append_player(player)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        from random import randint
        self.current_order().insert(randint(0, len(self.current_order())),
                                    player)

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        self.remove_last_appended_player()

    def on_player_turn_ended(self):
        self.next_player()

    def on_player_turn_rollback(self):
        self.previous_player()
