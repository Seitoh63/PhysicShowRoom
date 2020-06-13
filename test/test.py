import random
import sys
import time

import pygame

from src.mathematics import DirectedSegment
from src.physics.optics import PlaneMirror, Ray


def generate_segment():
    x0, y0 = random.randint(0, 500), random.randint(0, 500)
    x1, y1 = random.randint(0, 500), random.randint(0, 500)
    return DirectedSegment((x0, y0), (x1, y1))


def generate_ray():
    return Ray([generate_segment()])


def generate_mirror():
    return PlaneMirror(generate_segment())


def draw_ray(ray: Ray):
    for s in ray.directed_segments:
        pygame.draw.circle(win_surf, (0, 255, 0), s.first, 3)
        pygame.draw.circle(win_surf, (0, 0, 255), s.second, 3)
        pygame.draw.line(win_surf, (255, 255, 255), s.first, s.second)


def draw_rays(rays):
    for ray in rays:
        draw_ray(ray)


def draw_mirrors(mirrors):
    for mirror in mirrors:
        pygame.draw.line(win_surf, (0, 255, 255), mirror.p0(), mirror.p1())


pygame.init()
win_surf = pygame.display.set_mode((500, 500))

rays = []
mirrors = [generate_mirror()]

while True:

    rays.append(generate_ray())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    draw_rays(rays)
    draw_mirrors(mirrors)

    for i in range(len(rays)):
        ray = rays[i]
        for j in range(len(mirrors)):
            mirror = mirrors[j]
            reflection_vector = mirror.reflect(ray)
            if not reflection_vector: continue
            p = ray.directed_segments[-1].get_intersection_point(mirror.segment)

            s = reflection_vector.directed_segment(p, 200)
            pygame.draw.line(win_surf, (255, 255, 0), s.p0, s.p1)

    pygame.display.flip()
    time.sleep(1)
