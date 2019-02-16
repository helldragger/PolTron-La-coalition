from typing import Dict, Set, Tuple

from poltron_game.constants import COALITION, SOLO
from poltron_game.systems.positional_system import PositionalSystem


class TeamSystem(PositionalSystem):
    def __init__(self):
        super().__init__()
        self.team_members: Dict[int, Set[int]] = {
            COALITION: set(),
            SOLO:      set()
        }
        self.player_to_team: dict = {}

    def set_player_team(self, player: int, team: int):
        assert player not in self.player_to_team.keys()
        self.player_to_team[player] = team
        assert team in self.team_members.keys()
        assert player not in self.team_members[team]
        self.team_members[team].add(player)


    def get_player_team(self, player: int) -> int:
        return self.player_to_team[player]

    def get_team_positions(self, team: int) -> Set[Tuple[int, int]]:
        return self.pos_system.get_all_positions(team)

    def add_team_position(self, team: int, pos: Tuple[int, int]):
        self.pos_system.register_position(team, pos)

    def remove_team_position(self, team: int, pos: Tuple[int, int]):
        self.pos_system.unregister_position(team, pos)

    def get_team_count(self, team: int) -> int:
        return len(self.pos_system.get_all_positions(team))

    def get_all_teams_positions(self):
        return self.pos_system.get_all_types_to_positions_items()

    def on_player_move(self, player: int, old_pos: Tuple[int, int],
                       new_pos: Tuple[int, int]):
        team = self.get_player_team(player)
        self.remove_team_position(team, old_pos)
        self.add_team_position(team, new_pos)

    def on_player_kill(self, player: int, last_pos: Tuple[int, int]):
        team = self.get_player_team(player)
        self.remove_team_position(team, last_pos)

    def on_player_revival(self, player: int, last_pos: Tuple[int, int]):
        team = self.get_player_team(player)
        self.add_team_position(team, last_pos)

    def on_player_joined(self, player: int, team: int, pos: Tuple[int, int]):
        self.set_player_team(player, team)
        self.add_team_position(team, pos)

    def on_player_rollback(self, player: int, old_pos: Tuple[int, int],
                           new_pos: Tuple[int, int]):
        team = self.get_player_team(player)
        self.remove_team_position(team, new_pos)
        self.add_team_position(team, old_pos)
