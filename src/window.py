import sys
from collections import deque
from enum import Enum
from typing import Tuple

import pygame
from pygame.rect import Rect

from src.mathematics import Vector
from src.physics.world import World
from src.plot import draw_plot


class ParticleKinematic:
    """
    Class representing the kinematic at a given time of a particle
    """

    def __init__(self,
                 t=0.,
                 m=0.,
                 r: Vector = Vector(0., 0.),
                 v: Vector = Vector(0., 0.),
                 a: Vector = Vector(0., 0.)
                 ):
        self.t = t
        self.m = m
        self.r = r
        self.v = v
        self.a = a


class EntityType(Enum):
    Particle = 1,
    World = 2,


class Entity:
    """
    Class representing an entity for drawing purpose
    """

    def __init__(self, id, type: EntityType, kin: ParticleKinematic):
        self.id = id
        self.type = type
        self.kin = kin

    def __repr__(self):
        return self.type.name


class Plotter:
    """
    Class that show information on entities with different plots
    """
    text_width = 40
    font = pygame.font.SysFont("comicsansms", 8)
    queue_size = 1000
    point_to_skip = 0

    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        self.entity_dict = {}
        self.reference = (0, 0)

        self.skipped_points = -1
        self.fill_functions = {
            EntityType.World: self._fill_world_data,
            EntityType.Particle: self._fill_particle_data,
        }
        self.plot_functions = {
            EntityType.World: self._draw_world_plots,
            EntityType.Particle: self._draw_particle_plots,
        }

    def update(self, entities, observer: Entity):
        if 0 <= self.skipped_points < Plotter.point_to_skip:
            self.skipped_points += 1
            return

        self.skipped_points = 0

        for e in entities:
            self.fill_functions[e.type](e, observer, entities)

    def _fill_particle_data(self, e: Entity, observer: Entity, entities):
        if e.id not in self.entity_dict:
            self.entity_dict[e.id] = {
                "ts": deque(maxlen=Plotter.queue_size),
                "xs": deque(maxlen=Plotter.queue_size),
                "ys": deque(maxlen=Plotter.queue_size),
                "vys": deque(maxlen=Plotter.queue_size),
                "axs": deque(maxlen=Plotter.queue_size),
                "ays": deque(maxlen=Plotter.queue_size),
                "vxs": deque(maxlen=Plotter.queue_size),
            }

        self.entity_dict[e.id]["ts"].append(e.kin.t)
        self.entity_dict[e.id]["xs"].append(e.kin.r.x - observer.kin.r.x)
        self.entity_dict[e.id]["ys"].append(e.kin.r.y - observer.kin.r.y)
        self.entity_dict[e.id]["vxs"].append(e.kin.v.x - observer.kin.v.x)
        self.entity_dict[e.id]["vys"].append(e.kin.v.y - observer.kin.v.y)
        self.entity_dict[e.id]["axs"].append(e.kin.a.x - observer.kin.a.x)
        self.entity_dict[e.id]["ays"].append(e.kin.a.y - observer.kin.a.y)

    def _fill_world_data(self, world: Entity, observer: Entity, entities):
        if world.id not in self.entity_dict:
            self.entity_dict[world.id] = {
                "ts": deque(maxlen=Plotter.queue_size),
                "pxs": deque(maxlen=Plotter.queue_size),
                "pys": deque(maxlen=Plotter.queue_size),
                "Es": deque(maxlen=Plotter.queue_size)
            }
        E = 0
        p = Vector()
        for e in entities:
            if e.type != EntityType.Particle:
                continue

            v = (e.kin.v - observer.kin.v)
            E += 0.5 * e.kin.m * v.length() ** 2
            p += v * e.kin.m

        self.entity_dict[world.id]["ts"].append(world.kin.t)
        self.entity_dict[world.id]["Es"].append(E)
        self.entity_dict[world.id]["pxs"].append(p.x)
        self.entity_dict[world.id]["pys"].append(p.y)

    def draw(self, selected: Entity, entities):
        self.surf.fill((0, 0, 0))

        self._draw_selected_highlight(selected, entities)
        self._draw_entities_names(entities)
        self._draw_plots(selected)

        pygame.draw.rect(self.surf, (128, 0, 0), self.surf.get_rect(), 3)

    def reset(self):
        self.entity_dict = {}

    def _draw_selected_highlight(self, selected, entities):
        index = 0
        for i, p in enumerate(entities):
            if p.id == selected.id:
                index = i
                break

        text = Plotter.font.render(repr(entities[index]), True, (255, 255, 255))
        rect = text.get_rect()
        rect.top += 8 * index
        rect.left = 5
        pygame.draw.rect(self.surf, (128, 128, 128), rect)

    def _draw_entities_names(self, entities):
        h = 0
        for e in entities:
            text = Plotter.font.render(repr(e), True, (255, 255, 255))
            self.surf.blit(text, (5, h))
            h += 8

    def _draw_plots(self, selected):
        self.plot_functions[selected.type](selected)

    def _draw_particle_plots(self, selected):
        width, height = self.surf.get_rect().size
        plot_width = width - Plotter.text_width

        id = selected.id

        if id not in self.entity_dict:
            return

        ts = self.entity_dict[id]["ts"]
        xs = self.entity_dict[id]["xs"]
        ys = self.entity_dict[id]["ys"]
        vxs = self.entity_dict[id]["vxs"]
        vys = self.entity_dict[id]["vys"]
        axs = self.entity_dict[id]["axs"]
        ays = self.entity_dict[id]["ays"]

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

    def _draw_world_plots(self, selected):
        width, height = self.surf.get_rect().size
        plot_width = width - Plotter.text_width

        id = selected.id
        ts = self.entity_dict[id]["ts"]
        Es = self.entity_dict[id]["Es"]
        pxs = self.entity_dict[id]["pxs"]
        pys = self.entity_dict[id]["pys"]

        p_x0 = Plotter.text_width
        p_x1 = p_x0 + (plot_width // 2)
        p_w = plot_width // 2
        p_h = height // 3

        draw_plot(self.surf, pygame.Rect(p_x0, 0, p_w * 2, p_h), ts, Es, "E over time")
        draw_plot(self.surf, pygame.Rect(p_x0, p_h, p_w, p_h), ts, pxs, "px over time")
        draw_plot(self.surf, pygame.Rect(p_x1, p_h, p_w, p_h), ts, pys, "py over time")


class Viewer:
    """
    Class giving a view of the world
    """
    font = pygame.font.SysFont("comicsansms", 8)

    def __init__(self, surf: pygame.Surface, window):
        self.surf = surf
        self.window = window

        self.origin = (
            surf.get_rect().w // 2, surf.get_rect().h // 2)  # In the surface in pixel, coordinate of the origin

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

        if observer.type != EntityType.World:
            self.world_shift = observer.kin.r

        self._draw_selected_highlight(selected, world)
        self._draw_world_rectangle(world)
        self._draw_reference_axis(observer, world)
        self._draw_particles(world, observer)
        self._draw_rays(world, observer)
        self._draw_mirrors(world, observer)
        self._draw_surface_frame()

    def set_observer_shift(self, pos: Tuple[int, int]) -> None:
        x, y = self.world_shift
        ox, oy = self.origin
        sx, sy = self._pixel_to_world_len(pos[0] - ox), self._pixel_to_world_len(pos[1] - oy)
        self.world_shift = x + sx, y - sy

    def increase_scale(self):
        self.world_scale *= 2

    def decrease_scale(self):
        self.world_scale /= 2

    def _world_to_pixel_pos(self, world_r: Tuple[float, float], world_dim: Tuple[int, int]):
        ox, oy = self.origin
        owx, owy = self.world_shift[0], world_dim[1] - self.world_shift[1]
        owx, owy = self._world_to_pixel_len(owx), self._world_to_pixel_len(owy)
        wx, wy = world_r[0], world_dim[1] - world_r[1]
        return ox + self._world_to_pixel_len(wx) - owx, oy + self._world_to_pixel_len(wy) - owy

    def _world_to_pixel_len(self, world_len):
        return int(self.world_scale * world_len)

    def _pixel_to_world_len(self, pixel_len):
        return int(pixel_len / self.world_scale)

    def _draw_selected_highlight(self, observer, world):
        r = self._world_to_pixel_pos(observer.kin.r, world.rect.size)
        pygame.draw.circle(self.surf, (255, 255, 255), r, 6)

    def _draw_world_rectangle(self, world):
        x, y = self._world_to_pixel_pos((0, 0), world.rect.size)
        w, h = self._world_to_pixel_len(world.rect.w), self._world_to_pixel_len(world.rect.h)
        pygame.draw.rect(self.surf, (0, 128, 128), pygame.Rect(x, y - h, w, h), 3)

    def _draw_reference_axis(self, observer, world):
        x, y = self._world_to_pixel_pos(observer.kin.r, world.rect.size)
        pygame.draw.line(self.surf, (255, 255, 255), (x, y), (x + 10, y))
        pygame.draw.line(self.surf, (255, 255, 255), (x, y), (x, y + 10))
        text = Viewer.font.render("{:.2f}".format(10 / self.world_scale), True, (255, 255, 255))
        self.surf.blit(text, (x, y))

    def _draw_rays(self, world, observer):
        for ray in world.rays:
            for s in ray.directed_segments:
                x0, y0 = s.p0
                x1, y1 = s.p1
                r0 = self._world_to_pixel_pos((x0, y0), world.rect.size)
                r1 = self._world_to_pixel_pos((x1, y1), world.rect.size)
                r0 = int(r0[0]), int(r0[1])
                r1 = int(r1[0]), int(r1[1])
                pygame.draw.line(self.surf, (255, 255, 255), r0, r1, 1)

    def _draw_particles(self, world, observer):
        for p in world.particles:
            r = self._world_to_pixel_pos(p.r, world.rect.size)
            r = int(r[0]), int(r[1])
            v = self._world_to_pixel_len(p.v.x - observer.kin.v.x), self._world_to_pixel_len(p.v.y - observer.kin.v.y)
            v = int(v[0]), int(v[1])
            a = self._world_to_pixel_len(p.a.x - observer.kin.a.x), self._world_to_pixel_len(p.a.y - observer.kin.a.y)
            a = int(a[0]), int(a[1])
            self._draw_particle(r, v, a)

    def _draw_particle(self, r, v, a):

        pygame.draw.circle(self.surf, (255, 0, 0), r, 3)
        pygame.draw.line(self.surf, (0, 255, 0), r, (r[0] + v[0], r[1] - v[1]), 2)
        pygame.draw.line(self.surf, (0, 0, 255), r, (r[0] + a[0], r[1] - a[1]), 2)

    def _draw_surface_frame(self):
        pygame.draw.rect(self.surf, (128, 0, 0), self.surf.get_rect(), 3)

    def _draw_mirrors(self, world, observer):
        for mirror in world.mirrors:
            x0, y0, x1, y1 = mirror.segment
            r0 = self._world_to_pixel_pos((x0, y0), world.rect.size)
            r1 = self._world_to_pixel_pos((x1, y1), world.rect.size)
            r0 = int(r0[0]), int(r0[1])
            r1 = int(r1[0]), int(r1[1])
            pygame.draw.line(self.surf, (0, 255, 255), r0, r1, 1)


class Window:
    """
    Classe representing the window which will be a top container of shown elements.
    """

    viewer_ratio_rect = ((0., 0.), (0.5, 1.))
    plotter_ratio_rect = ((0.5, 0.), (0.5, 1.))

    def __init__(self, width: int = 1600, height: int = 1080):
        pygame.init()

        self.width, self.height = width, height
        self.surf = pygame.display.set_mode((self.width, self.height))

        self.viewer = Viewer(self._get_subsurface(Window.viewer_ratio_rect), self)
        self.plotter = Plotter(self._get_subsurface(Window.plotter_ratio_rect))

        self.selected_entity_index = 0
        self.reference_entity_index = 0
        self.entities = []

        self.previous_world_t = -1.

    def update(self, world: World, events):
        """ Update the visible elements with the given world """

        is_world_updated = self.previous_world_t != world.t
        if is_world_updated:
            self.previous_world_t = world.t

        self._handle_events(events)

        self.entities = self._get_entities(world)

        self.selected_entity_index %= len(self.entities)
        selected_entity = self.entities[self.selected_entity_index]
        reference_entity = self.entities[self.reference_entity_index]
        self.viewer.draw(world, reference_entity, selected_entity)

        if is_world_updated: self.plotter.update(self.entities, reference_entity)
        self.plotter.draw(selected_entity, self.entities)

        pygame.display.flip()

    def _handle_events(self, events):
        for event in events:

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

                if event.key == pygame.K_DOWN:
                    self.selected_entity_index += 1

                if event.key == pygame.K_UP:
                    self.selected_entity_index -= 1

                if event.key == pygame.K_SPACE:
                    self.reference_entity_index = self.selected_entity_index
                    self.plotter.reset()

                if event.key == pygame.K_KP_PLUS:
                    self.viewer.increase_scale()

                if event.key == pygame.K_KP_MINUS:
                    self.viewer.decrease_scale()

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

    def _get_entities(self, world):

        entities = [
            Entity(world.id,
                   EntityType.World,
                   ParticleKinematic(world.t, 0., Vector(world.rect.w // 2, world.rect.h // 2))
                   )
        ]

        for p in world.particles:
            entities.append(Entity(p.id, EntityType.Particle, ParticleKinematic(p.t, p.m, p.r, p.v, p.a)))
        return entities
