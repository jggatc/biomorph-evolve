#Biomorph Evolve - Copyright (C) 2017
#Released under the GPL3 License

from __future__ import division
import os, sys
if os.name in ('posix', 'nt', 'os2', 'ce', 'riscos'):
    import pygame
    platform = 'pc'
elif os.name == 'java':
    import pyj2d
    sys.modules['pygame'] = pyj2d
    pygame = pyj2d
    platform = 'jvm'
else:
    import pyjsdl as pygame
    platform = 'js'
Color = pygame.Color


class App(object):

    def __init__(self, function):
        self._fn = function
        self.quit = False
        if platform == 'js':
            self.run = self.run_js
            self.set_function = self.set_function_js

    def set_function(self, function):
        self._fn = function

    def set_function_js(self, function):
        self._fn = function
        pygame.display.setup(self._fn)

    def run(self):
        while not self.quit:
            self._fn()

    def run_js(self):
        pygame.display.setup(self._fn)

    def terminate(self):
        self.quit = True
        pygame.quit()


class Control(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.clock = pygame.time.Clock()
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.waiting = False
        pointer_cursor, wait_cursor = self.set_cursor()
        self.cursor = {False:pointer_cursor, True:wait_cursor}
        self.set_wait(False)
        self.quit = False

    def check_control(self):
        if not pygame.event.peek():
            return self.quit
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.matrix.restart()
                elif event.key == pygame.K_SPACE:
                    self.matrix.repeat = True
                elif event.key == pygame.K_ESCAPE:
                    self.quit = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.matrix.repeat = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.waiting:
                        self.matrix.biomorph_select(event.pos)
            elif event.type == pygame.QUIT:
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
            curs, mask = pygame.cursors.compile(pointer_cursor_strings, 'X', '.')
            pointer_cursor = ((24, 24), (0, 1), curs, mask)
            curs, mask = pygame.cursors.compile(wait_cursor_strings, 'X', '.')
            wait_cursor =  ((24, 24), (4, 2), curs, mask)
        elif platform == 'jvm':
            pointer_cursor = pygame.cursors.HAND_CURSOR
            wait_cursor = pygame.cursors.WAIT_CURSOR
        elif platform == 'js':
            pointer_cursor = 'pointer'
            wait_cursor = 'wait'
        return pointer_cursor, wait_cursor

    def set_wait(self, setting):
        self.waiting = setting
        if platform == 'pc':
            pygame.mouse.set_cursor(*self.cursor[self.waiting])
        else:
            pygame.mouse.set_cursor(self.cursor[self.waiting])
        return None

    def update(self):
        quit = self.check_control()
        self.clock.tick(60)
        return quit


class Renderer(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill(self.matrix.screen_color)
        self.screen.blit(self.background, (0,0))
        if platform == 'js':
            self.screen._strokestyle = None
        self.rect = self.screen.get_rect()
        self.rect_list = [self.rect]
        self.point_cache = PointCache()
        if platform in ('js','jvm'):
            pygame.draw.set_return(False)
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
            pygame.draw.aaline(image, color, pt1, pt2)
        image.unlock()
        self.point_cache.set(pt1)
        self.point_cache.set(pt2)

    def blit(self, image, pos):
        rect = self.screen.blit(image, pos)
        self.rect_list.append(rect)

    def draw_grid(self, grid, size, color):
        self.background.fill(self.matrix.screen_color)
        for pos in grid:
            pygame.draw.rect(self.background, color, (pos[0],pos[1],size[0],size[1]), 1)
        self.screen.blit(self.background, (0,0))
        self.rect_list = [self.rect]

    def clear(self):
        self.screen.blit(self.background, (0,0))
        self.rect_list = [self.rect]

    def blank(self):
        self.screen.fill(self.matrix.screen_color)
        self.update()

    def update(self):
        pygame.display.update()


class Config(object):

    def setup(self, w,h):
        pygame.init()
        pygame.display.set_mode((w,h))
        pygame.display.set_caption('Biomorph Evolve')
        if platform != 'js':
            pygame.display.set_icon(pygame.image.load('icon.png'))


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
            rect = pygame.Rect(x,y,w,h)
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

