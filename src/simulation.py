import sys

import pygame

from src.window import Window


class Simulation:
    def __init__(self, world):
        self.world = world
        self.viewer = Window()
        self.is_paused = False

    def run(self):
        clock = pygame.time.Clock()
        while True:

            dt = clock.tick() / 1000  # ellapsed time in seconds
            if not self.is_paused:
                self.world.update(dt)
            events = self._handle_events()
            self.viewer.update(self.world, events)

    def _handle_events(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            events.append(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAUSE:
                    self.is_paused = not self.is_paused
        return events


if __name__ == '__main__':
    Simulation().run()
