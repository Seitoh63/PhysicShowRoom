from typing import Tuple

import pygame

pygame.init()
n_x_tick = 5
n_y_tick = 5

tick_width = 3

ax_color = (255, 255, 255)
point_color = (255, 255, 255)
point_size = 2
margin_ratio = 10 / 100

tick_label_font = pygame.font.SysFont("comicsansms", 8)
tick_label_color = (255, 255, 255)
tick_label_format = '{:3.0f}'

title_font = pygame.font.SysFont("comicsansms", 12)
title_color = (255, 255, 255)


def _draw_x_ticks(plot_surf, p0, p1, x_range):
    x0, y0 = p0
    x1, y1 = p1
    minx, maxx = x_range

    for tick_index in range(1, n_x_tick + 1):
        x_tick = int(tick_index * (x1 - x0) / (n_x_tick + 1)) + x0
        pygame.draw.line(plot_surf, ax_color, (x_tick, y0 - tick_width), (x_tick, y0 + tick_width))

        x = (tick_index * (maxx - minx) / (n_x_tick + 1)) + minx
        x_label = tick_label_format.format(x)
        text = tick_label_font.render(x_label, True, tick_label_color)
        plot_surf.blit(text, (x_tick, y0 + tick_width))


def _draw_y_ticks(plot_surf, p0, p1, y_range):
    x0, y0 = p0
    x1, y1 = p1
    miny, maxy = y_range
    for tick_index in range(1, n_y_tick + 1):
        y_tick = y0 - int(tick_index * (y0 - y1) / (n_y_tick + 1))
        pygame.draw.line(plot_surf, ax_color, (x0 - tick_width, y_tick), (x0 + tick_width, y_tick))

        y = miny + (tick_index * (maxy - miny) / (n_x_tick + 1))
        y_label = tick_label_format.format(y)
        text = tick_label_font.render(y_label, True, tick_label_color)
        plot_surf.blit(text, (x0 - tick_width - text.get_rect().width, y_tick))


def _draw_axis(surf: pygame.Surface, p0: Tuple[int, int], p1: Tuple[int, int]) -> None:
    x0, y0 = p0
    x1, y1 = p1
    pygame.draw.line(surf, ax_color, (x0, y0), (x1, y0))
    pygame.draw.line(surf, ax_color, (x0, y0), (x0, y1))


def _draw_points(surf: pygame.Surface, xs, ys, p0, p1, minx, miny, lx, ly):
    x0, y0 = p0
    x1, y1 = p1

    previous_x_pixel, previous_y_pixel = 0, 0

    for p in zip(xs, ys):
        x, y = p
        x_pixel = int(x0 + (((x - minx) / lx) * (x1 - x0)))
        y_pixel = int(y0 + (((y - miny) / ly) * (y1 - y0)))

        if x_pixel == previous_x_pixel and y_pixel == previous_y_pixel:
            continue

        pygame.draw.circle(surf, point_color, (x_pixel, y_pixel), point_size)


def _draw_title(surf, rect, title):
    text = title_font.render(title, True, title_color)
    text_rect = text.get_rect()
    text_rect.midtop = (rect.width // 2, 0)
    surf.blit(text, text_rect)


def draw_plot(surf: pygame.Surface, rect: pygame.Rect, xs: list, ys: list, title: str):
    """
    Draw a plot with data xs and ys on surface surf in rectangle rect
    :param surf:
    :param rect:
    :param xs:
    :param ys:
    :param title:
    :return:
    """

    plot_surf = surf.subsurface(rect)
    w, h = rect.size
    x0, y0 = int(w * margin_ratio), int(h * (1 - margin_ratio))
    x1, y1 = int(w * (1 - margin_ratio)), int(h * margin_ratio)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    lx, ly = maxx - minx, maxy - miny

    _draw_axis(plot_surf, (x0, y0), (x1, y1))
    _draw_title(plot_surf, rect, title)

    if lx == 0. or ly == 0.:
        return

    _draw_x_ticks(plot_surf, (x0, y0), (x1, y0), (minx, maxx))
    _draw_y_ticks(plot_surf, (x0, y0), (x0, y1), (miny, maxy))
    _draw_points(plot_surf, xs, ys, (x0, y0), (x1, y1), minx, miny, lx, ly)
