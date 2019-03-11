import random
from typing import Dict, List, Tuple

from poltron_game.constants import COALITION, DOWN, LEFT, RIGHT, SOLO, UP
from poltron_game.systems.event import EventSystem
from poltron_game.systems.events.event import Event
from poltron_game.systems.events.game_ended import GameEndedEvent
from poltron_game.systems.events.player_joined import PlayerJoinedEvent
from poltron_game.systems.events.player_kill import PlayerKillEvent
from poltron_game.systems.events.player_move import PlayerMoveEvent
from poltron_game.systems.events.player_turn_ended import PlayerTurnEndedEvent
from poltron_game.systems.events.turn_ended import TurnEndedEvent
from poltron_game.systems.order import OrderSystem
from poltron_game.systems.player import PlayerSystem
from poltron_game.systems.rollback import RollbackSystem
from poltron_game.systems.team import TeamSystem
from poltron_game.systems.wall import WallSystem


"""
author: Alexis Mortelier
contributor: Vincent DE MENEZES
"""


class Game(object):

    def __init__(self, m: int, n: int, c: int, ds: int, dc: int):
        assert m > 0
        assert n > 0
        assert ds > 1
        assert dc > 0
        assert dc < ds
        assert c > 0
        self.m: int = m
        self.n: int = n
        self.ds: int = ds
        self.dc: int = dc
        self.c: int = c
        self.tick: int = 0
        self.victory: bool = False

        self.order_system: OrderSystem = OrderSystem(ds, dc)
        self.player_system: PlayerSystem = PlayerSystem()
        self.team_system: TeamSystem = TeamSystem()
        self.wall_system: WallSystem = WallSystem()
        from poltron_game.systems.log import LogSystem
        self.log_system: LogSystem = LogSystem(self, print_screen=False)

        self.event_system: EventSystem = EventSystem()
        self.rollback_system: RollbackSystem = RollbackSystem(self.event_system)

        self.event_system.register_system(self.wall_system)
        self.event_system.register_system(self.player_system)
        self.event_system.register_system(self.team_system)
        self.event_system.register_system(self.order_system)
        self.event_system.register_system(self.log_system)
        self.event_system.register_system(self.rollback_system)

    def _send_event(self, event: Event):
        self.event_system.send_event(event)

    def _generate_board_string(self) -> str:
        res = ""
        for row in range(self.m):
            for col in range(self.n):
                coord = (row, col)
                if coord in self.team_system.get_team_positions(COALITION):
                    res += "*"
                elif coord in self.team_system.get_team_positions(SOLO):
                    res += "%"
                elif self.wall_system.is_wall(coord):
                    res += "#"
                else:
                    res += "O"
                res += " "
            res += "\n"
        return res

    def _generate_players(self):
        row: List[int] = random.sample(range(0, self.m), self.c + 1)
        col: List[int] = random.sample(range(0, self.n), self.c + 1)
        pos: Tuple[int, int] = (row[0], col[0])
        self._send_event(PlayerJoinedEvent(0, SOLO, pos))

        for i in range(1, len(row)):
            pos = (row[i], col[i])
            self._send_event(PlayerJoinedEvent(i, COALITION, pos))

    def has_ended(self) -> bool:
        return self.team_system.get_team_count(
            SOLO) == 0 or self.team_system.get_team_count(COALITION) == 0

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.m and 0 <= pos[
            1] < self.n and not self.wall_system.is_wall(pos)

    @staticmethod
    def move_to_pos(coord: Tuple[int, int], direction: int) -> Tuple[int, int]:
        if direction == RIGHT:
            return coord[0], coord[1] + 1
        elif direction == LEFT:
            return coord[0], coord[1] - 1
        elif direction == UP:
            return coord[0] - 1, coord[1]
        elif direction == DOWN:
            return coord[0] + 1, coord[1]
        else:
            return coord

    def run(self):
        from poltron_ia.paranoid import algorithm_paranoid
        self._generate_players()
        team_depth: Dict[int, int] = {
            SOLO:      self.ds,
            COALITION: self.dc
        }
        while not self.has_ended():
            p: int = self.order_system.current_player()
            team: int = self.team_system.get_player_team(p)

            self.log_system.is_simulating = True

            move: int = algorithm_paranoid(self, team_depth.get(team), team, p)

            self.log_system.is_simulating = False

            self.play_player_turn(move)

    def play_player_turn(self, move: int):

        p: int = self.order_system.current_player()
        old_pos: Tuple[int, int] = self.player_system.get_player_position(p)

        new_pos: Tuple[int, int] = self.move_to_pos(old_pos, move)

        if not self.is_valid_position(new_pos):
            self._send_event(PlayerKillEvent(p, old_pos))
            if self.has_ended():
                self._send_event(PlayerTurnEndedEvent())
                self._send_event(GameEndedEvent())
                return
        else:
            self._send_event(PlayerMoveEvent(p, old_pos, new_pos))

        self._send_event(PlayerTurnEndedEvent())
        if self.order_system.is_new_rotation():
            self.tick += 1
            self._send_event(TurnEndedEvent())
