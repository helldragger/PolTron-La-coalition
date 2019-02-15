from typing import Tuple

from poltron_game.systems.updatable import Updatable


class OrderSystem(Updatable):
    def __init__(self):
        self.cursor: int = 0
        self.previous_order: list = []
        self.current_order: list = []
        self.next_order: list = []

    def next_player(self) -> int:
        self.cursor += 1
        if self.cursor >= len(self.current_order):
            self.cursor = 0
            self.previous_order = self.current_order
            self.current_order = self.next_order
            self.next_order = []
        return self.current_order[self.cursor]

    def previous_player(self) -> int:
        self.cursor -= 1
        if self.cursor <= -1:
            self.next_order = self.current_order
            self.current_order = self.previous_order
            self.previous_order = []
            self.cursor = len(self.current_order) - 1
        return self.current_order[self.cursor]

    def current_player(self) -> int:
        return self.current_order[self.cursor]

    def append_player(self, player):
        self.next_order.append(player)

    def remove_last_appended_player(self):
        self.next_order.pop(len(self.next_order) - 1)

    def is_new_rotation(self) -> bool:
        return self.cursor == 0

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.append_player(player)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        from random import randint
        self.current_order.insert(randint(0, len(self.current_order)), player)
