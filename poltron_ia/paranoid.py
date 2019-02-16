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
        "players": {
            COALITION: set(),
            SOLO:      set()
        },
        "scope":   {}
    }
    for team, positions in game.team_system.get_all_teams_positions():
        for position in positions:
            dictionary_map["scope"][position] = 0
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


def range_control(game: Game, initial_pos: Tuple[int, int], allies: int,
                  indicator: dict) -> dict:
    enemies: int = reverse_team(allies)
    stack: deque = deque()
    visited: set = set()
    stack.append(initial_pos)
    while stack:
        coord: Tuple[int, int] = stack.pop()
        visited.add(coord)
        for move in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            scope: int = indicator["scope"].get(coord) + 1
            pos: Tuple[int, int] = (coord[0] + move[0], coord[1] + move[1])
            if pos not in visited and game.is_valid_position(pos):
                if pos not in indicator["scope"]:
                    indicator["scope"][pos] = scope
                    indicator["players"][allies].add(pos)
                    stack.insert(0, pos)
                elif indicator["scope"].get(pos) >= scope:
                    if indicator["scope"].get(pos) > scope:
                        indicator["scope"][pos] = scope
                        stack.insert(0, pos)
                        if pos not in indicator["players"][allies]:
                            indicator["players"][allies].add(pos)
                    if pos in indicator["players"][enemies]:
                        indicator["players"][enemies].remove(pos)
    return indicator


def heuristic(game: Game, target_team: int) -> float:
    map_indicator: dict = init_dictionary(game)
    for team, positions in game.team_system.get_all_teams_positions():
        for pos in positions:
            map_indicator = range_control(game, pos, team, map_indicator)
    len_allies: int = len(map_indicator["players"][target_team])
    len_enemies: int = len(map_indicator["players"][reverse_team(target_team)])
    size: int = len_allies + len_enemies + 1
    h: float = len_allies / size * 100
    return h


def algorithm_paranoid(game, depth: int, team: int, player: int) -> int:
    _, move = alphabeta(game, depth, team, player, -1000, 1000)
    return move


def alphabeta(game: Game, depth: int, initial_team: int, p: int, a: int,
              b: int) -> Tuple[float, int]:
    if depth == 0 or game.has_ended():
        return heuristic(game, initial_team), NO_MOVE
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
