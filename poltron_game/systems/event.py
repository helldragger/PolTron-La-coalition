from typing import List

from poltron_game.systems.events.event import Event
from poltron_game.systems.updatable import Updatable


class EventSystem():

    def __init__(self):
        self.systems: List[Updatable] = []

    def register_system(self, system: Updatable):
        self.systems.append(system)

    def send_event(self, event: Event):
        for system in self.systems:
            event.process_func(system)
