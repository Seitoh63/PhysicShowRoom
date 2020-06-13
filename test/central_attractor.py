import random

from src.mathematics import Vector
from src.physics.mechanics import CentralForce, Particle
from src.physics.world import World
from src.simulation import Simulation

w = World((2000, 2000))
c = Vector(w.rect.w // 2, w.rect.h // 2)
w.forces.append(CentralForce(c, 10000.))

n_particles = 2
vmax = 100
for _ in range(n_particles):
    pos = random.randint(0, w.rect.w), random.randint(0, w.rect.h)
    s = random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)
    m = 1.
    w.add_particle(Particle(Vector(pos[0], pos[1]), Vector(s[0], s[1]), m))

Simulation(w).run()
