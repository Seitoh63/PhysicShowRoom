import math
import uuid

import pygame


class Particle:

    def __init__(self, pos, speed, m):
        self.id = uuid.uuid1()
        self.t = 0
        self.x, self.y = pos
        self.vx, self.vy = speed
        self.ax, self.ay = 0, 0
        self.m = m

    def update(self, dt, f):
        self.t += dt

        fx, fy = f
        self.ax = fx / self.m
        self.ay = fy / self.m
        self.vx += self.ax * dt
        self.vy += self.ay * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

    def pos(self):
        return int(self.x), int(self.y)

    def vel(self):
        return int(self.vx), int(self.vy)

    def accel(self):
        return int(self.ax), int(self.ay)


class World:

    def __init__(self, dim):
        self.rect = pygame.Rect((0, 0), dim)
        self.particles = []

    def add_particle(self, p):
        self.particles.append(p)

    def update(self, dt):

        xc , yc = self.rect.w//2, self.rect.h//2

        for p_i in range(len(self.particles)):
            p = self.particles[p_i]

            f = 1. /math.sqrt((xc - p.x) ** 2 + (yc - p.y) ** 2)
            f *= 10000
            fx = f * ((xc - p.x) / math.sqrt((xc - p.x) ** 2 + (yc - p.y) ** 2))
            fy = f * ((yc - p.y) / math.sqrt((xc - p.x) ** 2 + (yc - p.y) ** 2))

            p.update(dt, (fx, fy))
            p.x %= self.rect.w
            p.y %= self.rect.h
