import random

from src.mathematics import Vector
from src.physics.mechanics import ConstantForce, Particle
from src.physics.world import World
from src.simulation import Simulation

w = World((800, 600))
w.forces.append(ConstantForce(Vector(0, -10.)))

n_particles = 25
vmax = 50
for _ in range(n_particles):
    pos = 0., 0.
    s = random.uniform(0, vmax), random.uniform(0, vmax)
    m = 1.
    w.add_particle(Particle(Vector(0.,0.), Vector(s[0],s[1]), m))

Simulation(w).run()
