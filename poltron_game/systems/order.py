from typing import Tuple

from poltron_game.systems.updatable import Updatable


class OrderSystem(Updatable):
    def __init__(self):
        self.cursor: int = 0
        self.previous_previous_order: list = []
        self.previous_order: list = []
        self.current_order: list = []
        self.next_order: list = []
        self.next_next_order: list = []
    def next_player(self) -> int:
        self.cursor += 1
        if self.cursor >= len(self.current_order):
            self.cursor = 0
            self.previous_previous_order = self.previous_order.copy()
            self.previous_order = self.current_order.copy()
            self.current_order = self.next_order.copy()
            self.next_order = self.next_next_order.copy()
            self.next_next_order = []
        return self.current_order[self.cursor]

    def previous_player(self) -> int:
        self.cursor -= 1
        if self.cursor <= -1:
            self.next_next_order = self.next_order.copy()
            self.next_order = self.current_order.copy()
            self.current_order = self.previous_order.copy()
            self.previous_order = self.previous_previous_order.copy()
            self.previous_previous_order = []
            self.cursor = max(len(self.current_order) - 1, 0)
        return self.current_order[self.cursor]

    def current_player(self) -> int:
        return self.current_order[self.cursor]

    def append_player(self, player):
        self.next_order.append(player)

    def remove_last_appended_player(self):
        self.next_order.pop(len(self.next_order) - 1)

    def remove_appended_player(self, player: int):
        self.next_order.remove(player)

    def is_new_rotation(self) -> bool:
        return self.cursor == 0

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.append_player(player)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        from random import randint
        self.current_order.insert(randint(0, len(self.current_order)), player)

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        self.remove_last_appended_player()

    def on_player_turn_ended(self):
        self.next_player()

    def on_player_turn_rollback(self):
        self.previous_player()
