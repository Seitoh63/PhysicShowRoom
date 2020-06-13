import math


class Vector:
    def __init__(self, x: float = 0., y: float = 0.):
        self.x = x
        self.y = y

    def xy(self):
        return self.x, self.y

    def __getitem__(self, item):
        if item == 0 :
            return self.x
        if item == 1 :
            return self.y
        raise StopIteration()

    def unit_vector(self):
        norm = math.sqrt(self.x ** 2 + self.y ** 2)
        ux, uy = self.x / norm, self.y / norm
        return Vector(ux, uy)

    def length(self):
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def dot(self, vector):
        return (vector.x * self.x) + (vector.y * self.y)

    def cross_product(self, vector):
        return (vector.y * self.x) - (vector.x * self.y)

    def angle(self, vector):
        return math.acos(self.dot(vector) / (self.length() * vector.length()))

    def invert(self):
        return Vector(-self.x, -self.y)

    def scale_to(self, length: float):
        unit_vector = self.unit_vector()
        return unit_vector.scale_by(length)

    def scale_by(self, f: float):
        return Vector(self.x * f, self.y * f)

    def distance_to(self, v):
        return math.sqrt((self.x - v.x) ** 2 + (self.y - v.y) ** 2)

    def directed_segment(self, p0, length):
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



class Segment:
    def __init__(self, p0, p1):
        self.p0 = p0 if p0[0] < p1[0] else p1
        self.p1 = p1 if p0[0] < p1[0] else p0

    def x0(self):
        return self.p0[0]

    def y0(self):
        return self.p0[1]

    def x1(self):
        return self.p1[0]

    def y1(self):
        return self.p1[1]

    def get_coefs(self):
        x0, y0 = self.p0
        x1, y1 = self.p1

        a = (y1 - y0) / (x1 - x0) if x1 != x0 else float("inf")
        b = y1 - (a * x1)
        return a, b

    def get_intersection_point(self, segment):
        a1, b1 = self.get_coefs()
        a2, b2 = segment.get_coefs()

        if a1 == a2:
            return None

        x = (b2 - b1) / (a1 - a2)
        y = ((a2 * b1) - (a1 * b2)) / (a2 - a1)

        min_x = max(self.x0(), segment.x0())
        max_x = min(self.x1(), segment.x1())

        if not min_x <= x <= max_x:
            return None

        return x, y

    def get_colinear_vector(self):
        return Vector(self.x1() - self.x0(), self.y1() - self.y0()).unit_vector()

    def get_normal_vector(self):
        return Vector(self.y0() - self.y1(), self.x1() - self.x0()).unit_vector()


class DirectedSegment(Segment):
    """
    Class representing a segment with a direction
    """

    def __init__(self, p0, p1):
        super().__init__(p0, p1)
        self.first = p0
        self.second = p1

    def get_colinear_vector(self):
        return Vector(self.second[0] - self.first[0], self.second[1] - self.first[1]).unit_vector()
