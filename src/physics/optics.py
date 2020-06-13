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

    def reflect(self, ray_segment) -> Optional[Tuple[float, float, float]]:
        """ Return a vector representing the direction of the reflected ray. If no reflection, return None."""

        incident_vector = ray_segment.colinear_vector().invert()
        p = ray_segment.intersection_point(self.segment)
        if not p:
            return None

        r0 = ray_segment.first
        ray_segment.intersection_point(self.segment)
        if abs(r0[0] - p[0]) < 0.000001 and abs(r0[1] - p[1]) < 0.000001:
            return None

        reflection_angle = 2 * self._get_incidence_angle(incident_vector)
        reflection_vector = self._get_reflection_vector(reflection_angle, incident_vector)

        return p[0], p[1], - reflection_vector.angle_to_x()

    def _get_incidence_angle(self, incident_vector: Vector) -> float:
        normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector())
        inverted_normal_vec_angle = incident_vector.angle(self.segment.get_normal_vector().invert())
        return normal_vec_angle if abs(normal_vec_angle) < abs(inverted_normal_vec_angle) else inverted_normal_vec_angle

    def _get_reflection_vector(self, reflection_angle: float, incident_vector: Vector) -> Vector:
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
        self.n_rays = 16
        self.width, self.height = width, height

    def emit(self, particle: Particle, mirrors: [PlaneMirror]) -> [Ray]:
        """ Emit rays from a particle """
        angles = [math.pi * 2 * i / self.n_rays for i in range(self.n_rays)]
        rays = [self._generate_ray(angle, particle, mirrors) for angle in angles]
        return [ray for ray in rays if ray]

    def _generate_ray(self, angle: float, particle: Particle, mirrors: List[PlaneMirror]) -> Optional[Ray]:
        ray = Ray((particle.r.x, particle.r.y))

        while True:
            ray_segment = self._get_ray_segment(angle, ray)
            intersections = [self._intersect_with_world(ray_segment)]
            intersections.extend(self._intersect_with_mirrors(ray_segment, mirrors))

            x, y, angle = self._closest_intersection(ray.points[-1], intersections)
            ray.add((x, y))
            if angle is None or len(ray.points) > 100:
                if len(ray.points) > 100:
                    print(ray)
                return ray

    def _intersect_with_world(self, ray_segment: Segment) -> Tuple[float, float, float]:

        world_right = Segment((self.width, 0), (self.width, self.height))
        world_bottom = Segment((0, 0), (self.width, 0))
        world_top = Segment((0, self.height), (self.width, self.height))
        world_left = Segment((0, 0), (0, self.height))

        p = ray_segment.intersection_point(world_right)
        if p: return p[0], p[1], None
        p = ray_segment.intersection_point(world_top)
        if p: return p[0], p[1], None
        p = ray_segment.intersection_point(world_bottom)
        if p: return p[0], p[1], None
        p = ray_segment.intersection_point(world_left)
        if p: return p[0], p[1], None

        raise Exception()

    def _closest_intersection(self, point, intersections):
        x, y = point
        min_dist = float("inf")
        index = -1

        for i in range(len(intersections)):
            ix, iy, _ = intersections[i]
            d = math.sqrt((x - ix) ** 2 + (y - iy) ** 2)
            if d < min_dist:
                min_dist = d
                index = i

        return intersections[index]

    def _intersect_with_mirrors(self, ray_segment: DirectedSegment, mirrors: List[PlaneMirror]):
        intersections = []
        for mirror in mirrors:
            r = mirror.reflect(ray_segment)
            if r:
                intersections.append(r)
        return intersections

    def _get_ray_segment(self, angle: float, ray: Ray) -> Segment:
        v = Vector(math.cos(angle), math.sin(angle))
        v = v.scale_to(self.width * self.height)
        x, y = ray.points[-1]
        ray_segment = DirectedSegment((x, y), (x + v.x, y + v.y))
        return ray_segment
