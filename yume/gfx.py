import pygame
import numpy
from math import *
from pygame import Rect
from pygame.draw import *
from yume import *

#=============================================================================
#== Access functions

_gfx_cache = {}

class Drawable(object):
  graphic = None
  def __init__(self):
    self.x, self.y = 0, 0
    if self.graphic:
      self.gfx = get_gfx(self.graphic, (1, 1))
      self.rect = Rect(0, 0, self.gfx.width, self.gfx.height)
    self.rect = Rect(0, 0, 1, 1)

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()

class GFX(object):
  frames = 1
  current_frame = 0

  def next_frame(self):
    self.current_frame = (self.current_frame + 1) % len(self.surfaces)
    self.surface = self.surfaces[self.current_frame]

def get_gfx(name, args):
  key = (name, args)
  if key not in _gfx_cache:
    result = _draw_gfx(name, args)
    _gfx_cache[key] = result
    return result
  return _gfx_cache[key]

def _draw_gfx(cls, args):
  gfx = cls(args)
  surfaces = []
  for i in range(gfx.frames):
    surface = pygame.Surface((gfx.width, gfx.height))
    surface.set_colorkey((0, 0, 0))
    gfx.draw_frame(surface, i)
    surfaces.append(surface.convert_alpha())
  gfx.surfaces = surfaces
  gfx.surface = surfaces[gfx.current_frame]
  return gfx

#=============================================================================
#== Graphics

class Bullet(GFX):
  height = 5
  width = 5
  frames = 4
  foo = [(4, 2), (2, 4), (0, 2), (2, 0)]

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    line(surface, (205, 100, 255), (2, 2), self.foo[n])

class Bubble(GFX):
  height = 5
  width = 5
  frames = 4
#  foo = [(4, 2), (2, 4), (0, 2), (2, 0)]

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    circle(surface, (255, 255, 255), (2, 2), 2)
#    line(surface, (205, 100, 255), (2, 2), self.foo[n])

class MonsterGFX(GFX):
  height = 10
  width = 10
  frames = 1

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    circle(surface, (255, 0, 0), (5, 5), 5)
    circle(surface, (100, 100, 100), (5, 5), 5, 2)

class TowerBubbleGFX(GFX):
  height = 25
  width = 25
  frames = 1

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    circle(surface, (255, 255, 255), (12, 12), 12)
    circle(surface, (0, 255, 0), (12, 12), 12, 1)

class TowerTurretGFX(GFX):
  height = 25
  width = 25

  def __init__(self, args):
    self.scale, self.rotation = args
    self.recoil = 0
#    self.scale, self.rotation, self.recoil = args
    self.height = int(self.height * self.scale)
    self.width = int(self.width * self.scale)

  def draw_frame(self, surface, n):
    s = self.scale
    ellipse(surface, (100, 200, 0), Rect(2*s, 2*s, 22*s, 10*s))
#    surface.set_alpha(100)

class Background(GFX):
  height = 600
  width = 800
  frames = 32

  def __init__(self, args):
    self.scale, _ = args
    self.height = int(self.height * self.scale)
    self.width = int(self.width * self.scale)

  def draw_frame(self, surface, n):
    for j in range(20):
      points = []
      for i in range(120):
        points.append(((0 if i % 2 else 10) + j * 40, 5*i+n))
      for i in range(120):
        points.append(((0 if i % 2 else 10) + j * 40, 600-5*i+n+j))
      polygon(surface, (155, 0, 0), points)
#    line(surface, (255, 0, 0), (0, 0), (n * 10, 100))
#    line(surface, (255, 0, 0), (0, 0), (n * 10, 100))

  def draw_frame(self, surface, n):
#    colormap = 
#    ary = numpy.zeros((800, 600))
    x, y = surface.get_size()
    x /= 5
    y /= 5
    layer = pygame.Surface((x, y))
    ary = numpy.zeros((160, 120))
    for x in range(160):
      for y in range(120):
#        ary[x][y] = 1
        ary[x][y] = (sin((x+y+n/4.0)*pi/2) + 1) * 32
    pygame.surfarray.blit_array(layer, ary)
    layer = pygame.transform.scale(layer, surface.get_size())
    surface.blit(layer, (0, 0))
#    pygame.surfarray.blit_array(surface, ary)

class ManaBar(GFX):
  width = base_width = SCREEN_WIDTH
  height = 16
  frames = 1

  def __init__(self, args):
    self.scale = args[0]
    self.width = self.scale * self.base_width
    self.height = 16

  def draw_frame(self, surface, n):
    ary = numpy.zeros((self.width, self.height))
    for x in range(self.width):
      for y in range(self.height):
        if y == 0 or y == self.height - 1:
          ary[x][y] = 255
        elif x > self.width - 50:
          ary[x][y] = min(255, (sin((x/2+y)/2) + 1) * 96 + 64 + 3 * (x - self.width + 50))
        else:
          ary[x][y] = (sin((x/2+y)/2) + 1) * 96 + 64
    pygame.surfarray.blit_array(surface, ary)
#    rect(surface, (0, 0, 205 + int(50 * abs(sin(n*pi/100)))), Rect(0, 0, self.width, self.height))

