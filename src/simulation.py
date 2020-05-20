import pygame

from src.window import Window


class Simulation:
    def __init__(self, world=None):
        self.world = world if world else self._create_world()
        self.viewer = Window()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick() / 1000  # ellapsed time in seconds
            self.world.update(dt)
            self.viewer.update(self.world)


if __name__ == '__main__':
    Simulation().run()
