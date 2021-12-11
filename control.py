#Biomorph Evolve - Copyright (C) 2017
#Released under the GPL3 License

from __future__ import division
import os, sys
if os.name in ('posix', 'nt', 'os2', 'ce', 'riscos'):
    import pygame as pg
    platform = 'pc'
elif os.name == 'java':
    import pyj2d
    sys.modules['pg'] = pyj2d
    pg = pyj2d
    platform = 'jvm'
else:
    import pyjsdl as pg
    platform = 'js'
Color = pg.Color


class App(object):

    def __init__(self, fn):
        self._fn = fn
        self.quit = False
        if platform == 'js':
            self.run = self.run_js
            self.set_function = self.set_function_js

    def set_function_pc(self, fn):
        self._fn = fn

    def set_function_js(self, fn):
        self._fn = fn
        pg.set_callback(self._fn)

    def run(self):
        while not self.quit:
            self._fn()

    def run_js(self):
        pg.set_callback(self._fn)

    def terminate(self):
        self.quit = True
        pg.quit()


class Control(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.clock = pg.time.Clock()
        pg.event.set_blocked(pg.MOUSEMOTION)
        self.waiting = False
        pointer_cursor, wait_cursor = self.set_cursor()
        self.cursor = {False:pointer_cursor, True:wait_cursor}
        self.set_wait(False)
        self.quit = False

    def check_control(self):
        if not pg.event.peek():
            return self.quit
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.matrix.restart()
                elif event.key == pg.K_ESCAPE:
                    self.quit = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.waiting:
                        self.matrix.biomorph_select(event.pos)
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            self.matrix.repeat = True
                elif event.button == 3:
                    if not self.waiting:
                        if pg.key.get_mods() & pg.KMOD_SHIFT:
                            self.matrix.restart()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.matrix.repeat:
                        self.matrix.repeat = False
            elif event.type == pg.QUIT:
                self.quit = True
        return self.quit

    def set_cursor(self):
        if platform == 'pc':
            pointer_cursor_strings = (
              "                        ",
              ".                       ",
              "..                      ",
              ".X.                     ",
              ".XX.                    ",
              ".X.X.                   ",
              ".X..X.                  ",
              ".X...X.                 ",
              ".X....X.                ",
              ".X.....X.               ",
              ".X......X.              ",
              ".X.......X.             ",
              ".X........X.            ",
              ".X.........X.           ",
              ".X..........X.          ",
              ".X.......XXXX.          ",
              ".XXX....X....           ",
              "....X...X.              ",
              "    .X..X.              ",
              "    .X...X.             ",
              "     .X..X.             ",
              "     .XXX.              ",
              "      ...               ",
              "                        ",
            )
            wait_cursor_strings = (
              "                        ",
              "                        ",
              "     ..............     ",
              "    .XXXXXXXXXXXXXX.    ",
              "    .X            X.    ",
              "     .X..........X.     ",
              "      .X........X.      ",
              "       .X......X.       ",
              "        .X....X.        ",
              "         .X..X.         ",
              "          .XX.          ",
              "          .XX.          ",
              "          .XX.          ",
              "          .XX.          ",
              "         .X .X.         ",
              "        .X .  X.        ",
              "       .X   .  X.       ",
              "      .X   .    X.      ",
              "     .X..........X.     ",
              "    .X............X.    ",
              "    .XXXXXXXXXXXXXX.    ",
              "     ..............     ",
              "                        ",
              "                        ",
            )
            curs, mask = pg.cursors.compile(pointer_cursor_strings, 'X', '.')
            pointer_cursor = ((24, 24), (0, 1), curs, mask)
            curs, mask = pg.cursors.compile(wait_cursor_strings, 'X', '.')
            wait_cursor =  ((24, 24), (4, 2), curs, mask)
        elif platform == 'jvm':
            pointer_cursor = pg.cursors.HAND_CURSOR
            wait_cursor = pg.cursors.WAIT_CURSOR
        elif platform == 'js':
            pointer_cursor = 'pointer'
            wait_cursor = 'wait'
        return pointer_cursor, wait_cursor

    def set_wait(self, setting):
        self.waiting = setting
        if platform == 'pc':
            pg.mouse.set_cursor(*self.cursor[self.waiting])
        else:
            pg.mouse.set_cursor(self.cursor[self.waiting])
        return None

    def update(self):
        quit = self.check_control()
        self.clock.tick(60)
        return quit


class Renderer(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.screen = pg.display.get_surface()
        self.background = pg.Surface(self.screen.get_size())
        self.background.fill(self.matrix.screen_color)
        self.screen.blit(self.background, (0,0))
        if platform == 'js':
            self.screen._strokestyle = None
        self.rect = self.screen.get_rect()
        self.rect_list = [self.rect]
        self.point_cache = PointCache()
        if platform in ('js','jvm'):
            pg.draw.set_return(False)
        self.update()

    def render(self, biomorph, pos):
        x1 = biomorph.segments.x1
        y1 = biomorph.segments.y1
        x2 = biomorph.segments.x2
        y2 = biomorph.segments.y2
        idx = biomorph.segments.idx
        x, y, z = biomorph.segments.transform(self.matrix.size, pos)
        image = self.screen
        color = self.matrix.biomorph_color
        pt1 = self.point_cache.get()
        pt2 = self.point_cache.get()
        image.lock()
        for i in range(idx):
            pt1[0] = x1[i]//z+x
            pt1[1] = y1[i]//z+y
            pt2[0] = x2[i]//z+x
            pt2[1] = y2[i]//z+y
            pg.draw.aaline(image, color, pt1, pt2)
        image.unlock()
        self.point_cache.set(pt1)
        self.point_cache.set(pt2)

    def blit(self, image, pos):
        rect = self.screen.blit(image, pos)
        self.rect_list.append(rect)

    def draw_grid(self, grid, size, color):
        self.background.fill(self.matrix.screen_color)
        for pos in grid:
            pg.draw.rect(self.background, color, (pos[0],pos[1],size[0],size[1]), 1)
        self.screen.blit(self.background, (0,0))
        self.rect_list = [self.rect]

    def clear(self):
        self.screen.blit(self.background, (0,0))
        self.rect_list = [self.rect]

    def blank(self):
        self.screen.fill(self.matrix.screen_color)
        self.update()

    def update(self):
        pg.display.update()


class Config(object):

    def setup(self, w,h):
        pg.init()
        pg.display.set_mode((w,h))
        pg.display.set_caption('Biomorph Evolve')
        if platform != 'js':
            pg.display.set_icon(pg.image.load('icon.png'))


class RectCache(object):

    def __init__(self):
        self._cache = []

    def get(self, x, y, w, h):
        if self._cache:
            rect = self._cache.pop()
            rect.x = x
            rect.y = y
            rect.width = w
            rect.height = h
        else:
            rect = pg.Rect(x,y,w,h)
        return rect

    def set(self, rect):
        self._cache.append(rect)


class ListCache(object):

    def __init__(self):
        self._cache = []

    def get(self, x, y):
        if self._cache:
            lst = self._cache.pop()
            lst[0] = x
            lst[1] = y
        else:
            lst = [x,y]
        return lst

    def set(self, lst):
        self._cache.append(lst)


class PointCache(ListCache):

    def get(self):
        if self._cache:
            return self._cache.pop()
        else:
            return [0,0]
            


class DictCache(object):

    def __init__(self):
        self._cache = []

    def get(self):
        if self._cache:
            d = self._cache.pop()
        else:
            d = {}
            for i in range(1,10):
                d[i] = 0
        return d

    def set(self, d):
        self._cache.append(d)

