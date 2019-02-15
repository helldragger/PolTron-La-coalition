from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class TurnEndedEvent(Event):

    def process_func(self, system: Updatable):
        system.on_turn_ended()
