import math
from typing import List, Optional, Tuple

from src.mathematics import DirectedSegment, Segment, Vector
from src.physics.mechanics import Particle

Coefs = Tuple[float, float, float]


class Ray:
    """
    Class representing a ray of light
    """

    def __init__(self, point: Tuple[float, float]):
        self.points = [point]

    def add(self, point: Tuple[float, float]):
        self.points.append(point)

    def segments(self) -> List[DirectedSegment]:
        return [DirectedSegment(self.points[i], self.points[i + 1]) for i in range(len(self.points) - 1)]


class PlaneMirror:
    """
    Class representing a plane mirror
    """

    def __init__(self, segment: Segment):
        self.segment = segment

    def reflect(self, ray: Ray) -> Optional[Tuple[Tuple[float, float], Vector]]:
        """ Return a vector representing the direction of the reflected ray. If no reflection, return None."""

        ray_segment = ray.segments()[-1]
        incident_vector = ray_segment.colinear_vector().invert()
        p = ray_segment.intersection_point(self.segment)

        if not p:
            return None

        r0 = ray_segment.first
        if abs(r0[0] - p[0]) < 0.000001 and abs(r0[1] - p[1]) < 0.000001:
            return None

        reflection_angle = 2 * self._get_incidence_angle(incident_vector)
        reflection_vector = self._get_reflection_vector(reflection_angle, incident_vector)

        return p, reflection_vector

    def _get_incidence_angle(self, incident_vector: Vector) -> float:
        normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector())
        inverted_normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector().invert())

        if abs(normal_vec_angle) < abs(inverted_normal_vec_angle):
            angle = normal_vec_angle if incident_vector.cross_product(
                self.segment.get_normal_vector()) > 0 else - normal_vec_angle
        else:
            angle = inverted_normal_vec_angle if incident_vector.cross_product(
                self.segment.get_normal_vector().invert()) > 0 else - inverted_normal_vec_angle

        return angle

    def _get_reflection_vector(self, reflection_angle: float, incident_vector: Vector):
        cs = math.cos(reflection_angle)
        sn = math.sin(reflection_angle)
        x, y = incident_vector.x, incident_vector.y
        new_x = (x * cs) - (y * sn)
        new_y = (x * sn) + (y * cs)
        return Vector(new_x, new_y)


class RayEmitter:
    """
    Class that generate rays from punctual entities
    """

    def __init__(self, width, height):
        self.n_rays = 1024
        self.width, self.height = width, height

    def emit(self, particle: Particle, mirrors: [PlaneMirror]) -> [Ray]:
        """ Emit rays from a particle """
        angles = [((math.pi-0.00001) * 2 * i / (self.n_rays)) + 0.000001 for i in range(self.n_rays)]
        rays = [self._generate_ray(angle, particle, mirrors) for angle in angles]
        return [ray for ray in rays if ray]

    def _generate_ray(self, angle: float, particle: Particle, mirrors: List[PlaneMirror]) -> Optional[Ray]:
        ray = Ray((particle.r.x, particle.r.y))

        while True:

            self._propagate_ray(angle, ray)

            p0, p1 = ray.points[-2], ray.points[-1]
            if p0[0] == p1[0] and p0[1] == p1[1]:
                return None

            reflections = self._intersect_with_mirrors(ray, mirrors)
            if not reflections:
                return ray

            ray.points.pop()
            ray.add(reflections[0][0])
            angle = Vector(1., 0.).angle(reflections[0][1])
            angle = angle if Vector(1., 0.).cross_product(reflections[0][1]) > 0 else - angle

            if len(ray.points) > 100:
                return ray

    def _intersect_with_mirrors(self, ray: Ray, mirrors: List[PlaneMirror]) -> List[Tuple[Tuple[float, float], Vector]]:
        reflected_vectors = []
        for mirror in mirrors:
            r = mirror.reflect(ray)
            if r:
                reflected_vectors.append(r)
        return reflected_vectors

    def _get_line_equation_coefficients(self, p0: Tuple[float, float], p1: Tuple[float, float]) -> Coefs:
        x0, y0 = p0
        x1, y1 = p1

        if x1 - x0 == 0:
            return 0, 1., y0

        a = (y1 - y0) / (x1 - x0)
        c = y0 - a * x0
        return a, 1., c

    def _propagate_ray(self, angle: float, ray: Ray) -> None:

        if angle < 0.:
            angle += 2 * math.pi

        if angle > 2 * math.pi :
            angle -= 2 * math.pi

        x, y = ray.points[-1]
        a = math.tan(angle)
        b = y - (a * x)

        if a != 0:
            x_in_y0 = -b / a
            x_in_y1 = (self.height - b) / a
            y_in_x0 = b
            y_in_x1 = (a * self.width) + b
        else:
            y_in_x0 = y
            y_in_x1 = y

        if angle < math.pi / 2:
            if 0 <= y_in_x1 <= self.height:
                ray.add((self.width, y_in_x1))
                return

            if 0 <= x_in_y1 <= self.width:
                ray.add((x_in_y1, self.height))
                return

        if math.pi / 2 <= angle < math.pi:
            if 0 <= x_in_y1 <= self.width:
                ray.add((x_in_y1, self.height))
                return

            if 0 <= y_in_x0 <= self.height:
                ray.add((0., y_in_x0))
                return

        if math.pi <= angle < 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                ray.add((x_in_y0, 0.))
                return

            if 0 <= y_in_x0 <= self.height:
                ray.add((0., y_in_x0))
                return

        if angle >= 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                ray.add((x_in_y0, 0.))
                return

            if 0 <= y_in_x1 <= self.height:
                ray.add((self.width, y_in_x1))
                return
