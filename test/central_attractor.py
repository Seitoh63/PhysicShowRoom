import random

from pygame import Vector2

from src.physics import World, CentralForce, Particle
from src.simulation import Simulation

w = World((2000, 2000))
c = Vector2(w.rect.w // 2, w.rect.h // 2)
w.forces.append(CentralForce(c, 10000.))

n_particles = 25
vmax = 100
for _ in range(n_particles):
    pos = random.randint(0, w.rect.w), random.randint(0, w.rect.h)
    s = random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)
    m = 1.
    w.add_particle(Particle(Vector2(pos), Vector2(s), m))

Simulation(w).run()
