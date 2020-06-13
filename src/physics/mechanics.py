import uuid
from typing import Tuple

from pygame import Vector2

from src.mathematics import Vector


class Particle:
    """
    Class which represents a particle, i.e. a punctual mass. It is uniquely identified with an uuid.
    """

    def __init__(self, r: Vector, v: Vector, m: float):
        """
        :param r: position in world reference frame
        :param v: velocity in world reference frame
        :param m: mass
        """
        self.id = uuid.uuid1()
        self.t = 0  # living duration in seconds
        self.m = m

        self.previous_r = None
        self.r = r
        self.v = v
        self.a = Vector()

    def update(self, dt: float, f: Vector):
        self._update_euler(dt, f)

    def _update_euler(self, dt: float, f: Vector) -> None:
        self.t += dt
        self.previous_r = self.r

        self.a = f / self.m
        self.v += self.a * dt
        self.r += self.v * dt


class CentralForce:

    def __init__(self, center: Vector, magn: float):
        self.center = center
        self.magn = magn

    def applied_on(self, p):
        f = (self.center - p.r).unit_vector()
        f.scale_to(self.magn / self.center.distance_to(p.r))
        return f


class ConstantForce:

    def __init__(self, f: Vector):
        self.f = f

    def applied_on(self, p):
        return self.f
