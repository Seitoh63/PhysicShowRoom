import sys
from collections import deque

import pygame
from pygame.rect import Rect

from physics import Particle
from plot import draw_plot


class WorldGui:
    text_width = 100
    font = pygame.font.SysFont("comicsansms", 8)

    def __init__(self):
        self.particles = {}
        self.center = (0, 0)
        self.v = (0, 0)

    def _update(self, world):

        ox, oy = self.center

        for p in world.particles:
            if p.id not in self.particles:
                self.particles[p.id] = {
                    "ts": deque(maxlen=1000),
                    "xs": deque(maxlen=1000),
                    "ys": deque(maxlen=1000),
                    "vys": deque(maxlen=1000),
                    "axs": deque(maxlen=1000),
                    "ays": deque(maxlen=1000),
                    "vxs": deque(maxlen=1000),
                }
            self.particles[p.id]["ts"].append(p.t)
            self.particles[p.id]["xs"].append(p.x - ox)
            self.particles[p.id]["ys"].append(p.y - oy)
            self.particles[p.id]["vxs"].append(p.vx)
            self.particles[p.id]["vys"].append(p.vy)
            self.particles[p.id]["axs"].append(p.ax)
            self.particles[p.id]["ays"].append(p.ay)

    def draw(self, surf, world, selected_particle):

        self._update(world)

        width, height = surf.get_rect().size
        plot_width = width - WorldGui.text_width

        surf.fill((0, 0, 0))

        text = WorldGui.font.render("Particle", True, (255, 255, 255))
        rect = text.get_rect()

        rect.top += 8 * selected_particle
        rect.left = 5
        pygame.draw.rect(surf, (128, 128, 128), rect)

        h = 0
        for _ in self.particles:
            surf.blit(text, (5, h))
            h += 8

        p = world.particles[selected_particle]
        ts = self.particles[p.id]["ts"]
        xs = self.particles[p.id]["xs"]
        ys = self.particles[p.id]["ys"]
        vxs = self.particles[p.id]["vxs"]
        vys = self.particles[p.id]["vys"]
        axs = self.particles[p.id]["axs"]
        ays = self.particles[p.id]["ays"]

        p_x0 = WorldGui.text_width
        p_x1 = p_x0 + (plot_width // 2)
        p_w = plot_width // 2
        p_h = height // 3

        draw_plot(surf, pygame.Rect(p_x0, 0, p_w, p_h), ts, xs, "x over time")
        draw_plot(surf, pygame.Rect(p_x1, 0, p_w, p_h), ts, ys, "y over time")
        draw_plot(surf, pygame.Rect(p_x0, p_h, p_w, p_h), ts, vxs, "Vx over time")
        draw_plot(surf, pygame.Rect(p_x1, p_h, p_w, p_h), ts, vys, "Vy over time")
        draw_plot(surf, pygame.Rect(p_x0, p_h * 2, p_w, p_h), ts, axs, "Ax over time")
        draw_plot(surf, pygame.Rect(p_x1, p_h * 2, p_w, p_h), ts, ays, "Ay over time")

        pygame.draw.rect(surf, (128, 0, 0), surf.get_rect(), 3)

    def reset(self):
        self.particles = {}

    def set_center(self, pos):
        self.center = pos


class ParticleDrawer:

    def __init__(self, world_viewer):
        self.world_viewer = world_viewer

    def draw(self, surf, p):
        self._draw_particle(surf, p)
        self._draw_velocity(surf, p)
        self._draw_acceleration(surf, p)

    def _draw_particle(self, surf: pygame.Surface, p: Particle):
        x, y = self._get_pos(p)
        pygame.draw.circle(surf, (255, 0, 0), (x, y), 3)

    def _draw_velocity(self, surf, p: Particle):
        vx, vy = p.vel()
        vx, vy = self.world_viewer.world_to_pixel_len(vx), self.world_viewer.world_to_pixel_len(vy)
        x, y = self._get_pos(p)
        pygame.draw.line(surf, (0, 255, 0), (x, y), (x + vx, y + vy), 2)

    def _draw_acceleration(self, surf, p: Particle):
        ax, ay = p.accel()
        ax, ay = self.world_viewer.world_to_pixel_len(ax), self.world_viewer.world_to_pixel_len(ay)
        x, y = self._get_pos(p)
        pygame.draw.line(surf, (0, 0, 255), (x, y), (x + ax, y + ay), 2)

    def _get_pos(self, p):
        return self.world_viewer.world_to_pixel_pos(p.pos())


class WorldViewer:
    font = pygame.font.SysFont("comicsansms", 8)

    def __init__(self):
        self.particle_drawer = ParticleDrawer(self)
        self.world_point_at_center = (0, 0)
        self.origin = (0, 0)
        self.world_scale = 1

    def draw(self, surf, world, selected_particle_index, is_particle_origin):
        surf.fill((0, 0, 0))

        self.origin = (surf.get_rect().w // 2, surf.get_rect().h // 2)

        pos = world.particles[selected_particle_index].x , world.particles[selected_particle_index].y
        if is_particle_origin :
            self.world_point_at_center = pos
        x, y = self.world_to_pixel_pos(pos)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), 6)

        x, y = self.world_to_pixel_pos((0, 0))
        w, h = world.rect.w, world.rect.h
        w, h = self.world_to_pixel_len(w), self.world_to_pixel_len(h)
        if w <= 1 or h <= 1:
            return
        pygame.draw.rect(surf, (0, 128, 128), pygame.Rect(x, y, w, h), 3)

        ox, oy = self.origin
        pygame.draw.line(surf, (255, 255, 255), (ox, oy), (ox + 10, oy))
        pygame.draw.line(surf, (255, 255, 255), (ox, oy), (ox, oy + 10))
        text = WorldViewer.font.render("{:.2f}".format(10 / self.world_scale), True, (255, 255, 255))
        surf.blit(text, (ox, oy))

        for p in world.particles:
            self.particle_drawer.draw(surf, p)

        pygame.draw.rect(surf, (128, 0, 0), surf.get_rect(), 3)

    def world_to_pixel_pos(self, world_pos):
        ox, oy = self.origin
        owx, owy = self.world_point_at_center
        owx, owy = self.world_to_pixel_len(owx), self.world_to_pixel_len(owy)
        wx, wy = world_pos
        return ox + self.world_to_pixel_len(wx) - owx, oy + self.world_to_pixel_len(wy) - owy

    def world_to_pixel_len(self, world_len):
        return int(self.world_scale * world_len)

    def increase_scale(self):
        self.world_scale *= 2

    def decrease_scale(self):
        self.world_scale /= 2

    def set_center(self, pos):
        ox, oy = self.origin
        x, y = pos
        lx, ly = x - ox, y - oy
        lx, ly = int(lx // self.world_scale), int(ly // self.world_scale)
        wx, wy = self.world_point_at_center
        self.world_point_at_center = wx + lx, wy + ly


class Viewer:

    def __init__(self, width, height):
        pygame.init()

        self.width, self.height = width, height
        self.world_viewer = WorldViewer()
        self.world_gui = WorldGui()
        self.selected_particle = 0
        self.is_selected_particle_origin = False
        self.surf = pygame.display.set_mode((self.width, self.height))

    def update(self, world):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

                if event.key == pygame.K_DOWN:
                    self.selected_particle += 1

                if event.key == pygame.K_UP:
                    self.selected_particle -= 1

                if event.key == pygame.K_SPACE:
                    self.is_selected_particle_origin = not self.is_selected_particle_origin

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.set_center(event.pos)
                if event.button == 4:
                    self.world_viewer.increase_scale()
                if event.button == 5:
                    self.world_viewer.decrease_scale()

        self.selected_particle %= len(world.particles)

        rect_surf = self.surf.get_rect()
        viewer_rect_surf = Rect((0, 0), (rect_surf.width // 2, rect_surf.height))
        gui_rect_surf = Rect((rect_surf.width // 2, 0), (rect_surf.width // 2, rect_surf.height))
        viewer_surf = self.surf.subsurface(viewer_rect_surf)
        gui_surf = self.surf.subsurface(gui_rect_surf)

        self.world_viewer.draw(viewer_surf, world, self.selected_particle, self.is_selected_particle_origin)
        self.world_gui.set_center(self.world_viewer.world_point_at_center)
        self.world_gui.draw(gui_surf, world, self.selected_particle)

        pygame.display.flip()

    def set_center(self, pos):
        self.world_viewer.set_center(pos)
        self.world_gui.reset()
