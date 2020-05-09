import random
import time

from physics import World, Particle
from viewer import Viewer


def create_world():
    w = World((1000, 1000))
    n_particles = 20
    vmax = 100
    for _ in range(n_particles):
        pos = random.randint(0, w.rect.w), random.randint(0, w.rect.h)
        s = random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)
        m = 1.
        w.add_particle(Particle(pos, s, m))
    return w


def main():
    world = create_world()
    viewer = Viewer(1920, 1080)

    last_ts = time.time()
    while True:
        ts = time.time()
        dt = ts - last_ts
        last_ts = ts

        world.update(dt)
        viewer.update(world)


if __name__ == '__main__':
    main()
