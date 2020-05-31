import math
import uuid
from typing import Tuple

import pygame
from pygame import Vector2


class PlaneMirror:
    """
    Class representing a plane mirror
    """

    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1


class Ray:
    """
    Class representing a ray of light
    """

    def __init__(self, emitter, points):
        self.emitter = emitter
        self.points = points


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


class RayEmitter:
    """
    Class that generate rays from punctual entities
    """

    def __init__(self, width, height):
        self.n_rays = 100
        self.width, self.height = width, height

    def emit(self, particle: Particle, mirrors: [PlaneMirror]) -> [Ray]:
        return [self._generate_rays(2 * math.pi * i / self.n_rays, particle, mirrors) for i in range(self.n_rays)]

    def _generate_rays(self, angle, particle, mirrors):
        ray = self._generate_straight_ray(angle, particle)
        for mirror in mirrors :
            ma,mb,mc = self._get_line_equation_coefficients(mirror.p0, mirror.p1)
            ra, rb, rc = self._get_line_equation_coefficients(ray.points[-2], ray.points[-1])
        return ray
    def _get_line_equation_coefficients(self, p0, p1):
        x0, y0 = p0
        x1, y1 = p1
        a = (y1 - y0) / (x1 - x0)
        c = y0 - a * x0
        return a, 1., c

    def _generate_straight_ray(self, angle, particle):
        x, y = (particle.r.x, particle.r.y)
        a = math.tan(angle)
        b = y - (a * x)

        if a != 0:
            x_in_y0 = -b / a
            x_in_y1 = (self.height - b) / a
            y_in_x0 = b
            y_in_x1 = (a * self.width) + b
        else:
            x_in_y0 = x
            x_in_y1 = x

        if angle <= math.pi / 2:
            if 0 <= x_in_y1 <= self.width:
                return Ray(particle, [(x, y), (x_in_y1, self.height)])

            if 0 <= y_in_x1 <= self.height:
                return Ray(particle, [(x, y), (self.width, y_in_x1)])

        if math.pi / 2 < angle <= math.pi:
            if 0 <= x_in_y1 <= self.width:
                return Ray(particle, [(x, y), (x_in_y1, self.height)])

            if 0 <= y_in_x0 <= self.height:
                return Ray(particle, [(x, y), (0, y_in_x0)])

        if math.pi < angle <= 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                return Ray(particle, [(x, y), (x_in_y0, 0)])

            if 0 <= y_in_x0 <= self.height:
                return Ray(particle, [(x, y), (0, y_in_x0)])

        if angle > 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                return Ray(particle, [(x, y), (x_in_y0, 0)])

            if 0 <= y_in_x1 <= self.height:
                return Ray(particle, [(x, y), (self.width, y_in_x1)])


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

    def _compute_force_on(self, p: Particle):
        f = Vector2()
        for force in self.forces:
            f += force.applied_on(p)
        return f

    def _handle_out_of_world(self, p: Particle) -> None:

        if self.is_removed_if_out_of_world:

            if not 0 < p.r.x < self.rect.w:
                self.particles.remove(p)
                return

            if not 0 < p.r.y < self.rect.h:
                self.particles.remove(p)
        else:
            p.r.x %= self.rect.w
            p.r.y %= self.rect.h

    def _emit_rays(self):
        ray_emitter = RayEmitter(self.rect.w, self.rect.h)
        self.rays = [ray_emitter.emit(p, self.mirrors) for p in self.particles]
        self.rays = [y for x in self.rays for y in x]
