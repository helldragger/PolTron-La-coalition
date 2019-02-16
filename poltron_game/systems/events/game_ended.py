from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class GameEndedEvent(Event):

    def process_func(self, system: Updatable):
        system.on_game_ended()
