import uuid
from typing import Tuple

import pygame
from pygame import Vector2


class Particle:
    """
    Class which represents a particle, i.e. a punctual mass. It is uniquely identified with an uuid.
    """

    def __init__(self, r: Vector2, v: Vector2, m: float):
        """
        :param r: position in world reference frame
        :param v: velocity in world reference frame
        :param m: mass
        """
        self.id = uuid.uuid1()
        self.t = 0  # living duration in seconds
        self.m = m

        self.previous_r = None
        self.r = Vector2(r)
        self.v = Vector2(v)
        self.a = Vector2()

    def update(self, dt: float, f: Vector2):
        self._update_euler(dt, f)

    def _update_euler(self, dt: float, f: Vector2) -> None:
        self.t += dt
        self.previous_r = self.r

        self.a = f / self.m
        self.v += self.a * dt
        self.r += self.v * dt


class CentralForce:

    def __init__(self, center: Vector2, magn: float):
        self.center = center
        self.magn = magn

    def applied_on(self, p):
        f = (self.center - p.r).normalize()
        f.scale_to_length(self.magn / self.center.distance_to(p.r))
        return f


class ConstantForce:

    def __init__(self, f: Vector2):
        self.f = f

    def applied_on(self, p):
        return self.f


class World:
    """
    Top class for the physics simulations. It handles the main loop of updates for each entity. It also shows
    functions to add or remove entities in the world
    """

    def __init__(self, dim: Tuple[int, int]):
        self.rect = pygame.Rect((0, 0), dim)
        self.particles = []
        self.forces = []
        self.id = uuid.uuid1()
        self.t = 0

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

    def _compute_force_on(self, p: Particle):
        f = Vector2()
        for force in self.forces:
            f += force.applied_on(p)
        return f

    def _handle_out_of_world(self, p: Particle) -> None:
        p.r.x %= self.rect.w
        p.r.y %= self.rect.h
