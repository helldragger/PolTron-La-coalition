from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class PlayerTurnRollbackEvent(Event):

    def process_func(self, system: Updatable):
        system.on_player_turn_rollback()
