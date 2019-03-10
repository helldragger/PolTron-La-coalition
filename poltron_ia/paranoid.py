import random
from collections import deque
from typing import List, Tuple

from poltron_game.Game import Game
from poltron_game.constants import *


"""
        author: Vincent DE MENEZES
"""


def print_map_scope(scope: dict, len_row: int, len_col: int) -> None:
    grid: list = [0] * len_row
    for i in range(len(grid)):
        grid[i] = [0] * len_col
    for (row, col) in scope:
        grid[row][col] = scope.get((row, col))
    for i in range(len(grid)):
        print(grid[i])


def init_dictionary(game: Game) -> dict:
    dictionary_map: dict = {
        "area":    {
            COALITION: set(),
            SOLO:      set()
        },
        "scope":   {},
        "stack":   {
            COALITION: set(),
            SOLO:      set()
        },
        "visited": {
            COALITION: set(),
            SOLO:      set()
        }
    }

    for team, players in game.team_system.get_all_teams_positions():
        for p in players:
            dictionary_map["scope"][p] = 0
            dictionary_map["stack"][team].append(p)
    return dictionary_map


def random_move(game: Game, p: int) -> int:
    move: List[int] = [RIGHT, LEFT, UP, DOWN]
    random.shuffle(move)
    for sens in move:
        if game.is_valid_position(
                game.move_to_pos(game.player_system.get_player_position(p),
                                 sens)):
            return sens
    return RIGHT


def reverse_team(team: int) -> int:
    if team == COALITION:
        return SOLO
    return COALITION


def range_control(game: Game, current_depth: int) -> int:
    distances: dict = {}

    areas: dict = {
        SOLO:      set(),
        COALITION: set()
    }

    stacks: dict = {
        SOLO:      deque(),
        COALITION: deque()
    }

    visited: dict = {
        SOLO:      set(),
        COALITION: set()
    }

    count: int = (current_depth) * 2

    pos_solo: Tuple[int, int] = game.player_system.get_solo_player_position()
    x_solo, y_solo = pos_solo
    manhattan_distance = lambda pos: abs(x_solo - pos[0]) + abs(y_solo - pos[1])
    for team, players in game.team_system.get_all_teams_positions():
        for p in players:
            if manhattan_distance(p) <= count:
                distances[p] = 0
                stacks[team].append(p)

    while stacks[SOLO]:
        for team in game.team_system.get_all_teams():
            enemies = reverse_team(team)
            if stacks[team]:
                coord = stacks[team].pop()
                visited[team].add(coord)
                current_distance = distances.get(coord) + 1
                for move in {(1, 0), (-1, 0), (0, 1), (0, -1)}:
                    pos = (coord[0] + move[0], coord[1] + move[1])
                    if game.is_valid_position(pos) and pos not in visited[team]:
                        if pos not in distances:
                            distances[pos] = current_distance
                            areas[team].add(pos)
                            stacks[team].insert(0, pos)
                        elif distances[pos] >= current_distance:
                            if distances[pos] > current_distance:
                                distances[pos] = current_distance
                                stacks[team].insert(0, pos)
                                if not pos in areas[team]:
                                    areas[team].add(pos)
                            if pos in areas[enemies]:
                                areas[enemies].remove(pos)
    return len(areas[SOLO])


def heuristic(game: Game, target_team: int, current_depth: int) -> float:
    area_solo = range_control(game, current_depth)
    map_area = (game.m * game.m) - game.wall_system.count()
    if target_team == SOLO:
        return (area_solo / map_area) * 100
    else:
        return (1 - (area_solo / map_area)) * 100


def algorithm_paranoid(game, depth: int, team: int, player: int) -> int:
    _, move = alphabeta(game, depth, team, player, -1000, 1000)
    return move


def alphabeta(game: Game, depth: int, initial_team: int, p: int, a: int,
              b: int) -> Tuple[float, int]:
    pos_solo: Tuple[int, int] = game.player_system.get_solo_player_position()
    x_solo, y_solo = pos_solo
    manhattan_distance = lambda pos: abs(x_solo - pos[0]) + abs(y_solo - pos[1])
    position = game.player_system.get_player_position(p)
    if depth == 0 or game.has_ended() or manhattan_distance(
            position) > depth * 2:
        return heuristic(game, initial_team, depth), NO_MOVE
    team: int = game.team_system.get_player_team(p)

    best: int = -1000

    sens: int = NO_MOVE
    for move in [RIGHT, LEFT, UP, DOWN]:

        if game.has_ended():
            continue

        game.play_player_turn(move)
        next_player: int = game.order_system.current_player()
        next_player_team: int = game.team_system.get_player_team(next_player)
        if next_player_team != team:
            v, _ = alphabeta(game, depth - 1, initial_team, next_player,
                             -1 * a, -1 * b)
            v = -v
        else:
            v, _ = alphabeta(game, depth, initial_team, next_player,
                             a, b)
        game.rollback_system.rollback_last_turn()

        if v > best:
            best = v
            sens = move
        if best > a:
            a = best
        if a >= b:
            return best, sens

    if sens == NO_MOVE:
        sens = random_move(game, p)
    return best, sens
