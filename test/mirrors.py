from src.mathematics import Segment, Vector
from src.physics.mechanics import Particle
from src.physics.optics import PlaneMirror
from src.physics.world import World
from src.simulation import Simulation

w = World((800, 600))

m = 1.
w.add_particle(Particle(Vector(100., 200.), Vector(0, 0), m))

w.mirrors.append(PlaneMirror(Segment((0, 300), (400, 0))))

Simulation(w).run()
