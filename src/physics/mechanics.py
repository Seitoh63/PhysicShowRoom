import abc
import uuid

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

        self.r = r
        self.v = v
        self.a = Vector()

    def update(self, dt: float, f: Vector) -> None:
        """
        Update the particle following Newton mechanics
        """
        self._update_euler(dt, f)

    def _update_euler(self, dt: float, f: Vector) -> None:
        self.t += dt

        self.a = f / self.m
        self.v += self.a * dt
        self.r += self.v * dt


class Force(abc.ABC):
    """ Abstract class representing a force"""

    @abc.abstractmethod
    def apply_on(self, p: Particle) -> Vector:
        pass


class CentralForce(Force):
    """
    Class representing a central force
    """

    def __init__(self, center: Vector, magnitude: float):
        self.center = center
        self.magn = magnitude

    def apply_on(self, p: Particle) -> Vector:
        """Apply the force on a given particle"""
        f = (self.center - p.r).unit_vector()
        f = f.scale_to(self.magn / self.center.distance_to(p.r))
        return f


class ConstantForce(Force):
    """
    Class representing a constant force
    """

    def __init__(self, f: Vector):
        self.f = f

    def apply_on(self, p: Particle) -> Vector:
        """Apply the force on a given particle"""

        return self.f
