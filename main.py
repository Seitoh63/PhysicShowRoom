import random

import pygame

from physics import World, Particle
from window import Window
from pygame import Vector2

def create_world():
    w = World((2000, 2000))
    n_particles = 5
    vmax = 100
    for _ in range(n_particles):
        pos = random.randint(0, w.rect.w), random.randint(0, w.rect.h)
        s = random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)
        m = 1.
        w.add_particle(Particle(Vector2(pos), Vector2(s), m))
    return w


def main():
    world = create_world()
    viewer = Window()

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick() / 1000  # ellapsed time in seconds
        world.update(dt)
        viewer.update(world)


if __name__ == '__main__':
    main()
