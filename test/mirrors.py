import random

from pygame import Vector2

from src.physics import World, Particle, ConstantForce
from src.simulation import Simulation

w = World((800, 600))

n_particles = 3
vmax = 50
for _ in range(n_particles):
    pos = 0., 0.
    s = random.uniform(0, vmax), random.uniform(0, vmax)
    m = 1.
    w.add_particle(Particle(Vector2(pos), Vector2(s), m))

Simulation(w).run()
