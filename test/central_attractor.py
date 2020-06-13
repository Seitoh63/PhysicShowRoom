import random

from src.mathematics import Vector, Segment
from src.physics.mechanics import CentralForce, Particle
from src.physics.optics import PlaneMirror
from src.physics.world import World
from src.simulation import Simulation

w = World((2000, 2000))
c = Vector(w.rect.w // 2, w.rect.h // 2)
w.forces.append(CentralForce(c, 10000.))

n_particles = 1
vmax = 100
for _ in range(n_particles):
    pos = random.randint(0, w.rect.w), random.randint(0, w.rect.h)
    s = random.uniform(-vmax, vmax), random.uniform(-vmax, vmax)
    m = 1.
    w.add_particle(Particle(Vector(pos[0], pos[1]), Vector(s[0], s[1]), m))
w.mirrors.append(PlaneMirror(Segment((250, 250), (750, 750))))
w.mirrors.append(PlaneMirror(Segment((250, 750), (750, 250))))
w.mirrors.append(PlaneMirror(Segment((1250, 1250), (1750, 1750))))
w.mirrors.append(PlaneMirror(Segment((1250, 1750), (1750, 1250))))

w.mirrors.append(PlaneMirror(Segment((1250, 250), (1750, 750))))
w.mirrors.append(PlaneMirror(Segment((1250, 750), (1750, 250))))
w.mirrors.append(PlaneMirror(Segment((250, 1250), (750, 1750))))
w.mirrors.append(PlaneMirror(Segment((250, 1750), (750, 1250))))
Simulation(w).run()
