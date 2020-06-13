import uuid
from typing import Tuple

import pygame

from src.mathematics import Vector
from src.physics.mechanics import Particle
from src.physics.optics import RayEmitter


class World:
    """
    Top class for the physics simulations. It handles the main loop of updates for each entity. It also shows
    functions to add or remove entities in the world
    """

    def __init__(self, dim: Tuple[int, int]):
        self.rect = pygame.Rect((0, 0), dim)
        self.particles = []
        self.mirrors = []
        self.rays = []
        self.forces = []
        self.id = uuid.uuid1()
        self.t = 0

        self.is_removed_if_out_of_world = True

    def add_particle(self, p: Particle) -> None:
        """
        :param p: particle to be added to the world
        """
        self.particles.append(p)

    def update(self, dt: float) -> None:
        """
        Evolve the world for a given amount of time
        :param dt: evolution time in seconds
        """
        self.t += dt

        forces = []
        for p in self.particles:
            forces.append(self._compute_force_on(p))

        for i, p in enumerate(self.particles):
            p.update(dt, forces[i])
            self._handle_out_of_world(p)

        self._emit_rays()

    def _compute_force_on(self, p: Particle) -> Vector:
        f = Vector()
        for force in self.forces:
            f += force.apply_on(p)
        return f

    def _handle_out_of_world(self, p: Particle) -> None:

        if self.is_removed_if_out_of_world:

            if not 0 <= p.r.x <= self.rect.w:
                self.particles.remove(p)
                return

            if not 0 <= p.r.y <= self.rect.h:
                self.particles.remove(p)
        else:
            p.r.x %= self.rect.w
            p.r.y %= self.rect.h

    def _emit_rays(self) -> None:
        ray_emitter = RayEmitter(self.rect.w, self.rect.h)
        self.rays = [ray_emitter.emit(p, self.mirrors) for p in self.particles]
        self.rays = [y for x in self.rays for y in x]
