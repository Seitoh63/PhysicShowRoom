import math
from typing import List, Optional

from src.mathematics import DirectedSegment, Segment, Vector
from src.physics.mechanics import Particle


class Ray:
    """
    Class representing a ray of light
    """

    def __init__(self, directed_segments: List[DirectedSegment]):
        self.directed_segments = directed_segments


class PlaneMirror:
    """
    Class representing a plane mirror
    """

    def __init__(self, segment: Segment):
        self.segment = segment

    def p0(self):
        return self.segment.p0

    def p1(self):
        return self.segment.p1

    def segment(self):
        return self.segment

    def reflect(self, ray: Ray) -> Optional[Vector]:
        ray_segment = ray.directed_segments[-1]
        incident_vector = ray_segment.get_colinear_vector().invert()
        p = ray_segment.get_intersection_point(self.segment)

        if not p:
            return None

        reflection_angle = 2 * self._get_incidence_angle(incident_vector)
        reflection_vector = self._get_reflection_vector(reflection_angle, incident_vector)

        return reflection_vector

    def _get_incidence_angle(self, incident_vector):
        normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector())
        inverted_normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector().invert())

        if abs(normal_vec_angle) < abs(inverted_normal_vec_angle):
            angle = normal_vec_angle if incident_vector.cross_product(
                self.segment.get_normal_vector()) > 0 else - normal_vec_angle
        else:
            angle = inverted_normal_vec_angle if incident_vector.cross_product(
                self.segment.get_normal_vector().invert()) > 0 else - inverted_normal_vec_angle

        return angle

    def _get_reflection_vector(self, reflection_angle, incident_vector):
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
        self.n_rays = 128
        self.width, self.height = width, height

    def emit(self, particle: Particle, mirrors: [PlaneMirror]) -> [Ray]:
        # angles = [0, 2 * math.pi * 1 / 4.]
        # return [self._generate_rays(angle, particle, mirrors) for angle in angles]
        return [self._generate_rays(2 * math.pi * i / self.n_rays, particle, mirrors) for i in range(self.n_rays)]

    def _generate_rays(self, angle, particle, mirrors : List[PlaneMirror]):
        ray = self._generate_straight_ray(angle, particle)

        intersection_points = []
        for mirror in mirrors:
            ray_segment = ray.directed_segments[-1]
            mirror_segment = mirror.segment
            intersection = ray_segment.get_intersection_point(mirror_segment)
            if intersection:
                intersection_points.append(intersection)

        if intersection_points == []:
            return ray

        px, py = particle.r
        x, y = intersection_points[0]
        min_d = math.sqrt((px - x) ** 2 + (py - y) ** 2)
        closest_intersection_point = intersection_points[0]
        print(closest_intersection_point)
        return ray

    def _get_line_equation_coefficients(self, p0, p1):
        x0, y0 = p0
        x1, y1 = p1

        if x1 - x0 == 0:
            return 0, 1., y0

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
            y_in_x0 = y
            y_in_x1 = y

        if angle < math.pi / 2:
            if 0 <= y_in_x1 <= self.height:
                return Ray([DirectedSegment((x, y), (self.width, y_in_x1))])

            if 0 <= x_in_y1 <= self.width:
                return Ray( [DirectedSegment((x, y), (x_in_y1, self.height))])

        if math.pi / 2 <= angle < math.pi:
            if 0 <= x_in_y1 <= self.width:
                return Ray([DirectedSegment((x, y), (x_in_y1, self.height))])

            if 0 <= y_in_x0 <= self.height:
                return Ray([DirectedSegment((x, y), (0, y_in_x0))])

        if math.pi <= angle < 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                return Ray([DirectedSegment((x, y), (x_in_y0, 0))])

            if 0 <= y_in_x0 <= self.height:
                return Ray([DirectedSegment((x, y), (0, y_in_x0))])

        if angle >= 3. / 2. * math.pi:
            if 0 <= x_in_y0 <= self.width:
                return Ray([DirectedSegment((x, y), (x_in_y0, 0))])

            if 0 <= y_in_x1 <= self.height:
                return Ray([DirectedSegment((x, y), (self.width, y_in_x1))])
