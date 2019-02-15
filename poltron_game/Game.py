import random
from typing import Tuple

from poltron_game.constants import COALITION, DOWN, LEFT, RIGHT, SOLO, UP
from poltron_game.systems.event import EventSystem
from poltron_game.systems.events.event import Event
from poltron_game.systems.events.player_joined import PlayerJoinedEvent
from poltron_game.systems.events.player_kill import PlayerKillEvent
from poltron_game.systems.events.player_move import PlayerMoveEvent
from poltron_game.systems.events.turn_ended import TurnEndedEvent
from poltron_game.systems.order import OrderSystem
from poltron_game.systems.player import PlayerSystem
from poltron_game.systems.team import TeamSystem
from poltron_game.systems.wall import WallSystem


"""
	author: Alexis Mortelier
        contributor: Vincent DE MENEZES
"""


class Game(object):

    def __init__(self, m, n, c, ds, dc):
        self.ds = ds
        self.dc = dc
        self.m = m
        self.n = n
        self.c = c
        self.tick = 0

        self.order_system: OrderSystem = OrderSystem()
        self.player_system: PlayerSystem = PlayerSystem()
        self.team_system: TeamSystem = TeamSystem()
        self.wall_system: WallSystem = WallSystem()

        from poltron_game.systems.log import LogSystem
        self.log_system: LogSystem = LogSystem(self, print_screen=True)

        self.event_system: EventSystem = EventSystem()
        self.event_system.register_system(self.wall_system)
        self.event_system.register_system(self.player_system)
        self.event_system.register_system(self.team_system)
        self.event_system.register_system(self.order_system)
        self.event_system.register_system(self.log_system)

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
        row = random.sample(range(0, self.m), self.c + 1)
        col = random.sample(range(0, self.n), self.c + 1)
        pos = (row[0], col[0])
        self._send_event(PlayerJoinedEvent(0, SOLO, pos))

        for i in range(1, len(row)):
            pos = (row[i], col[i])
            self._send_event(PlayerJoinedEvent(i, COALITION, pos))


    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    def has_ended(self) -> bool:
        return self.team_system.get_team_count(
            SOLO) == 0 or self.team_system.get_team_count(COALITION) == 0

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.m and pos[
            1] < self.n and not self.wall_system.is_wall(pos)

    def move_to_pos(self, coord: Tuple[int, int], direction: int) -> Tuple[
        int, int]:
        if direction == RIGHT:
            return (coord[0], coord[1] + 1)
        elif direction == LEFT:
            return (coord[0], coord[1] - 1)
        elif direction == UP:
            return (coord[0] - 1, coord[1])
        elif direction == DOWN:
            return (coord[0] + 1, coord[1])


    def run(self):
        from poltron_ia.paranoid import algorithm_paranoid
        self._generate_players()
        team_depth = {
            SOLO:      self.ds,
            COALITION: self.dc
        }
        while not self.has_ended():
            p = self.order_system.current_player()
            old_pos = self.player_system.get_player_position(p)
            team = self.team_system.get_player_team(p)
            old_value = self.log_system.print_screen
            self.log_system.print_screen = False
            move = algorithm_paranoid(self, team_depth.get(team), team, p)
            self.log_system.print_screen = old_value
            new_pos = self.move_to_pos(old_pos, move)

            if not self.is_valid_position(new_pos):
                self._send_event(PlayerKillEvent(p, old_pos))
                if self.has_ended():
                    break
            else:
                self._send_event(PlayerMoveEvent(p, old_pos, new_pos))

            self.order_system.next_player()
            if self.order_system.is_new_rotation():
                self.tick += 1

    def play_player_turn(self, move: int):
        p = self.order_system.current_player()
        old_pos = self.player_system.get_player_position(p)
        new_pos = self.move_to_pos(old_pos, move)
        if not self.is_valid_position(new_pos):
            self._send_event(PlayerKillEvent(p, old_pos))
            if self.has_ended():
                return
        else:
            self._send_event(PlayerMoveEvent(p, old_pos, new_pos))

        self.order_system.next_player()
        if self.order_system.is_new_rotation():
            self.tick += 1
            self._send_event(TurnEndedEvent())
