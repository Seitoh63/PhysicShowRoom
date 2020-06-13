from src.mathematics import Segment, Vector
from src.physics.mechanics import Particle
from src.physics.optics import PlaneMirror
from src.physics.world import World
from src.simulation import Simulation

w = World((800, 600))

m = 1.
w.add_particle(Particle(Vector(400., 300.), Vector(0, 0), m))

w.mirrors.append(PlaneMirror(Segment((0, 150), (200, 0))))
w.mirrors.append(PlaneMirror(Segment((650, 0), (800, 150))))
w.mirrors.append(PlaneMirror(Segment((650, 600), (800, 450))))
w.mirrors.append(PlaneMirror(Segment((0, 450), (200, 600))))

Simulation(w).run()
