import sys
from collections import deque
from typing import Tuple

import pygame
from pygame import Vector2
from pygame.rect import Rect

import physics
from plot import draw_plot


class Entity:

    def __init__(self, id, r: Vector2, v: Vector2 = Vector2(0., 0.), a: Vector2 = Vector2(0., 0.)):
        self.id = id
        self.r = pygame.Vector2(r)
        self.v = pygame.Vector2(v)
        self.a = pygame.Vector2(a)


class Particle:

    def __init__(self, p: physics.Particle):
        self.rx = p.r.x
        self.ry = p.r.y
        self.vx = p.v.x
        self.vy = p.v.y
        self.ax = p.a.x
        self.ay = p.a.y

    def r(self):
        return self.rx, self.ry

    def v(self):
        return self.vx, self.vy

    def a(self):
        return self.ax, self.ay


class Plotter:
    """
    Class that show information on entities with different plots
    """
    text_width = 100
    font = pygame.font.SysFont("comicsansms", 8)
    queue_size = 500
    point_to_skip = 0

    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        self.particles = {}
        self.reference = (0, 0)

        self.skipped_points = -1

    def update(self, world, observer: Entity):
        if 0 <= self.skipped_points < Plotter.point_to_skip:
            self.skipped_points += 1
            return

        self.skipped_points = 0

        for p in world.particles:
            if p.id not in self.particles:
                self.particles[p.id] = {
                    "ts": deque(maxlen=Plotter.queue_size),
                    "xs": deque(maxlen=Plotter.queue_size),
                    "ys": deque(maxlen=Plotter.queue_size),
                    "vys": deque(maxlen=Plotter.queue_size),
                    "axs": deque(maxlen=Plotter.queue_size),
                    "ays": deque(maxlen=Plotter.queue_size),
                    "vxs": deque(maxlen=Plotter.queue_size),
                }
            self.particles[p.id]["ts"].append(p.t)
            self.particles[p.id]["xs"].append(p.r.x - observer.r.x)
            self.particles[p.id]["ys"].append(p.r.y - observer.r.y)
            self.particles[p.id]["vxs"].append(p.v.x - observer.v.x)
            self.particles[p.id]["vys"].append(p.v.y - observer.v.y)
            self.particles[p.id]["axs"].append(p.a.x - observer.a.x)
            self.particles[p.id]["ays"].append(p.a.y - observer.a.y)

    def draw(self, world, observer: Entity):
        self.surf.fill((0, 0, 0))

        self._draw_selected_highlight(world, observer)
        self._draw_entities_names()
        self._draw_plots(observer)

        pygame.draw.rect(self.surf, (128, 0, 0), self.surf.get_rect(), 3)

    def reset(self):
        self.particles = {}

    def set_center(self, pos):
        self.center = pos

    def _draw_selected_highlight(self, world, observer):
        index = 0
        for i, p in enumerate(world.particles):
            if p.id == observer.id:
                index = i
                break

        text = Plotter.font.render("Particle", True, (255, 255, 255))
        rect = text.get_rect()
        rect.top += 8 * index
        rect.left = 5
        pygame.draw.rect(self.surf, (128, 128, 128), rect)

    def _draw_entities_names(self):
        text = Plotter.font.render("Particle", True, (255, 255, 255))
        h = 0
        for _ in self.particles:
            self.surf.blit(text, (5, h))
            h += 8

    def _draw_plots(self, observer):
        width, height = self.surf.get_rect().size
        plot_width = width - Plotter.text_width

        id = observer.id
        ts = self.particles[id]["ts"]
        xs = self.particles[id]["xs"]
        ys = self.particles[id]["ys"]
        vxs = self.particles[id]["vxs"]
        vys = self.particles[id]["vys"]
        axs = self.particles[id]["axs"]
        ays = self.particles[id]["ays"]

        p_x0 = Plotter.text_width
        p_x1 = p_x0 + (plot_width // 2)
        p_w = plot_width // 2
        p_h = height // 3

        draw_plot(self.surf, pygame.Rect(p_x0, 0, p_w, p_h), ts, xs, "x over time")
        draw_plot(self.surf, pygame.Rect(p_x1, 0, p_w, p_h), ts, ys, "y over time")
        draw_plot(self.surf, pygame.Rect(p_x0, p_h, p_w, p_h), ts, vxs, "Vx over time")
        draw_plot(self.surf, pygame.Rect(p_x1, p_h, p_w, p_h), ts, vys, "Vy over time")
        draw_plot(self.surf, pygame.Rect(p_x0, p_h * 2, p_w, p_h), ts, axs, "Ax over time")
        draw_plot(self.surf, pygame.Rect(p_x1, p_h * 2, p_w, p_h), ts, ays, "Ay over time")


class Viewer:
    """
    Class giving a view of the world
    """
    font = pygame.font.SysFont("comicsansms", 8)

    def __init__(self, surf: pygame.Surface, window):
        self.surf = surf
        self.window = window

        self.origin = (surf.get_rect().w // 2, surf.get_rect().h // 2)  # In the surface, coordinate of the origin

        self.world_shift = (0, 0)  # shift between the center of the view and the origin of the world
        self.world_scale = 1  # n_pixel = world_length * world_scale

    def draw(self, world, observer: Entity, selected: Entity) -> None:
        """
        Draw the view of the world
        :param selected:
        :param world: world to be drawn
        :param observer :
        """

        self.surf.fill((0, 0, 0))

        self.world_shift = observer.r.xy

        self._draw_selected_highlight(selected)
        self._draw_world_rectangle(world)
        self._draw_reference_axis(observer)
        self._draw_particles(world, observer)
        self._draw_surface_frame()

    def set_observer_shift(self, pos: Tuple[int, int]) -> None:
        x, y = self.world_shift
        ox, oy = self.origin
        sx, sy = self._pixel_to_world_len(pos[0] - ox), self._pixel_to_world_len(pos[1] - oy)
        self.world_shift = x + sx, y + sy

    def increase_scale(self):
        self.world_scale *= 2

    def decrease_scale(self):
        self.world_scale /= 2

    def _world_to_pixel_pos(self, world_r: Tuple[float, float]):
        ox, oy = self.origin
        owx, owy = self.world_shift
        owx, owy = self._world_to_pixel_len(owx), self._world_to_pixel_len(owy)
        wx, wy = world_r
        return ox + self._world_to_pixel_len(wx) - owx, oy + self._world_to_pixel_len(wy) - owy

    def _world_to_pixel_len(self, world_len):
        return int(self.world_scale * world_len)

    def _pixel_to_world_len(self, pixel_len):
        return int(pixel_len / self.world_scale)

    def _draw_selected_highlight(self, observer):
        r = self._world_to_pixel_pos(observer.r.xy)
        pygame.draw.circle(self.surf, (255, 255, 255), r, 6)

    def _draw_world_rectangle(self, world):
        x, y = self._world_to_pixel_pos((0, 0))
        w, h = self._world_to_pixel_len(world.rect.w), self._world_to_pixel_len(world.rect.h)
        pygame.draw.rect(self.surf, (0, 128, 128), pygame.Rect(x, y, w, h), 3)

    def _draw_reference_axis(self, observer):
        x, y = self._world_to_pixel_pos(observer.r.xy)
        pygame.draw.line(self.surf, (255, 255, 255), (x, y), (x + 10, y))
        pygame.draw.line(self.surf, (255, 255, 255), (x, y), (x, y + 10))
        text = Viewer.font.render("{:.2f}".format(10 / self.world_scale), True, (255, 255, 255))
        self.surf.blit(text, (x, y))

    def _draw_particles(self, world, observer):
        for pp in world.particles:
            p = Particle(pp)
            p.rx, p.ry = self._world_to_pixel_pos(p.r())
            p.rx, p.ry = int(p.rx), int(p.ry)
            p.vx, p.vy = self._world_to_pixel_len(p.vx - observer.v.x), self._world_to_pixel_len(p.vy - observer.v.y)
            p.vx, p.vy = int(p.vx), int(p.vy)
            p.ax, p.ay = self._world_to_pixel_len(p.ax - observer.a.x), self._world_to_pixel_len(p.ay - observer.a.y)
            p.ax, p.ay = int(p.ax), int(p.ay)
            self._draw_particle(p)

    def _draw_particle(self, p):
        pygame.draw.circle(self.surf, (255, 0, 0), p.r(), 3)
        pygame.draw.line(self.surf, (0, 255, 0), p.r(), (p.rx + p.vx, p.ry + p.vy), 2)
        pygame.draw.line(self.surf, (0, 0, 255), p.r(), (p.rx + p.ax, p.ry + p.ay), 2)

    def _draw_surface_frame(self):
        pygame.draw.rect(self.surf, (128, 0, 0), self.surf.get_rect(), 3)


class Window:
    """
    Classe representing the window which will be a top container of shown elements.
    """

    viewer_ratio_rect = ((0., 0.), (0.5, 1.))
    plotter_ratio_rect = ((0.5, 0.), (0.5, 1.))

    def __init__(self, width: int = 1920, height: int = 1080):
        pygame.init()

        self.width, self.height = width, height
        self.surf = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

        self.viewer = Viewer(self._get_subsurface(Window.viewer_ratio_rect), self)
        self.plotter = Plotter(self._get_subsurface(Window.plotter_ratio_rect))

        self.selected_particle = 0
        self.reference_particle = 0

    def update(self, world):
        """ Update the visible elements with the given world """

        self._handle_events()

        self.selected_particle %= len(world.particles)
        selected_p = world.particles[self.selected_particle]
        reference_p = world.particles[self.reference_particle]
        selected = Entity(selected_p.id, selected_p.r, selected_p.v, selected_p.a)
        reference = Entity(reference_p.id, reference_p.r, reference_p.v, reference_p.a)

        self.plotter.update(world, reference)

        self.viewer.draw(world, reference, selected)
        self.plotter.draw(world, selected)

        pygame.display.flip()

    def _handle_events(self):
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
                    self.reference_particle = self.selected_particle
                    self.plotter.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.viewer.set_observer_shift(event.pos)
                if event.button == 4:
                    self.viewer.increase_scale()
                if event.button == 5:
                    self.viewer.decrease_scale()

    def _get_subsurface(self, ratio_rect: Tuple[Tuple[float, float], Tuple[float, float]]):
        rect_surf = self.surf.get_rect()

        rect_sub_surf = Rect((0, 0), (0, 0))
        rect_sub_surf.x = int(ratio_rect[0][0] * rect_surf.w)
        rect_sub_surf.w = int(ratio_rect[1][0] * rect_surf.w)
        rect_sub_surf.y = int(ratio_rect[0][1] * rect_surf.h)
        rect_sub_surf.h = int(ratio_rect[1][1] * rect_surf.h)

        return self.surf.subsurface(rect_sub_surf)
