from collections import deque
from typing import Tuple

from poltron_game.systems.event import EventSystem
from poltron_game.systems.events.player_revival import PlayerRevivalEvent
from poltron_game.systems.events.player_rollback import PlayerRollbackEvent
from poltron_game.systems.events.player_turn_rollback import \
    PlayerTurnRollbackEvent
from poltron_game.systems.events.turn_rollback import TurnRollbackEvent
from poltron_game.systems.updatable import Updatable


class RollbackSystem(Updatable):

    def __init__(self, event_system: EventSystem):
        self.turn_actions: deque = deque()
        self.previous_turn_actions: deque = deque()
        self.event_system: EventSystem = event_system

    def rollback_last_turn(self):
        assert len(self.previous_turn_actions) > 0
        actions: deque = self.previous_turn_actions.pop()
        for _ in range(len(actions)):
            event = actions.pop()
            self.event_system.send_event(event)

    def on_player_turn_ended(self):
        self.turn_actions.append(PlayerTurnRollbackEvent())

        self.previous_turn_actions.append(self.turn_actions.copy())
        self.turn_actions.clear()

    def on_turn_ended(self):
        self.turn_actions.append(TurnRollbackEvent())

    def on_player_kill(self, player: int, last_pos: Tuple[int, int]):
        self.turn_actions.append(PlayerRevivalEvent(player, last_pos))

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        self.turn_actions.append(PlayerRollbackEvent(player, old_pos, new_pos))
