from __future__ import annotations

import math
from typing import Tuple, Optional


class Vector:
    """ Class representing a 2d Vector"""

    def __init__(self, x: float = 0., y: float = 0.):
        self.x = x
        self.y = y

    def unit_vector(self) -> Vector:
        """ Return a vector in same direction as self and with length 1"""
        norm = math.sqrt(self.x ** 2 + self.y ** 2)
        ux, uy = self.x / norm, self.y / norm
        return Vector(ux, uy)

    def length(self) -> float:
        """ Return length of the vector"""
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def dot_product(self, vector: Vector) -> float:
        """ Return dot product with the given vector"""
        return (vector.x * self.x) + (vector.y * self.y)

    def cross_product(self, vector: Vector) -> float:
        """ Return cross product with the given vector """
        return (vector.y * self.x) - (vector.x * self.y)

    def angle(self, vector: Vector) -> float:
        """ Return angle of the vector with respect to x axis """
        c= self.dot_product(vector) / (self.length() * vector.length())
        c = 1. if c > 1. else c
        c = -1. if c < -1. else c
        return math.acos(c)

    def invert(self) -> Vector:
        """ Return a vector with opposite direction"""
        return Vector(-self.x, -self.y)

    def scale_to(self, length: float) -> Vector:
        """ Return a vector in same direction scaled to given length"""
        unit_vector = self.unit_vector()
        return unit_vector.scale_by(length)

    def scale_by(self, f: float) -> Vector:
        """ Return a vector scaled by the factor given"""
        return Vector(self.x * f, self.y * f)

    def distance_to(self, v: Vector) -> float:
        """ Return the length of the difference of the two vectors """
        return math.sqrt((self.x - v.x) ** 2 + (self.y - v.y) ** 2)

    def directed_segment(self, p0: Tuple[float, float], length: float) -> DirectedSegment:
        """ Return a directed segment from the given point in direction of the vector"""
        x1 = p0[0] + (self.unit_vector().x * length)
        y1 = p0[1] + (self.unit_vector().y * length)
        return DirectedSegment(p0, (x1, y1))

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other: float):
        return Vector(self.x / other, self.y / other)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        raise StopIteration()


class Segment:
    """ Class representing a segment"""

    def __init__(self, p0: Tuple[float, float], p1: Tuple[float, float]):
        self.p0 = p0 if p0[0] < p1[0] else p1
        self.p1 = p1 if p0[0] < p1[0] else p0

    def x0(self) -> float:
        return self.p0[0]

    def y0(self) -> float:
        return self.p0[1]

    def x1(self) -> float:
        return self.p1[0]

    def y1(self) -> float:
        return self.p1[1]

    def coefficients(self) -> Tuple[float, float]:
        """Return the coefficients of the line equation"""
        x0, y0 = self.p0
        x1, y1 = self.p1

        a = (y1 - y0) / (x1 - x0) if x1 != x0 else float("inf")
        b = y1 - (a * x1)
        return a, b

    def intersection_point(self, segment: Segment) -> Optional[Tuple[float, float]]:
        """ Return the intersection point between the 2 segments"""
        a1, b1 = self.coefficients()
        a2, b2 = segment.coefficients()

        if a1 == a2:
            return None

        x = (b2 - b1) / (a1 - a2)
        y = ((a2 * b1) - (a1 * b2)) / (a2 - a1)

        min_x = max(self.x0(), segment.x0())
        max_x = min(self.x1(), segment.x1())

        if not min_x <= x <= max_x:
            return None

        return x, y

    def colinear_vector(self) -> Vector:
        """ Get a colinear vector to the segment"""
        return Vector(self.x1() - self.x0(), self.y1() - self.y0()).unit_vector()

    def get_normal_vector(self) -> Vector:
        """ Get a normal vector to the segment"""
        return Vector(self.y0() - self.y1(), self.x1() - self.x0()).unit_vector()

    def __getitem__(self, item):
        if item == 0:
            return self.x0()
        if item == 1:
            return self.y0()
        if item == 2:
            return self.x1()
        if item == 3:
            return self.y1()

        raise StopIteration()


class DirectedSegment(Segment):
    """
    Class representing a segment with a direction
    """

    def __init__(self, p0: Tuple[float, float], p1: Tuple[float, float]):
        super().__init__(p0, p1)
        self.first = p0
        self.second = p1

    def colinear_vector(self) -> Vector:
        """ Get a colinear vector to the segment in the good direction"""
        return Vector(self.second[0] - self.first[0], self.second[1] - self.first[1]).unit_vector()
