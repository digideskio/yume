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
    surfaces = _draw_gfx(name, args)
    _gfx_cache[key] = surfaces
  else:
    surfaces = _gfx_cache[key]
  gfx = name(args)
  gfx.surfaces = surfaces
  gfx.surface = surfaces[gfx.current_frame]
  return gfx

def _draw_gfx(cls, args):
  gfx = cls(args)
  surfaces = []
  for i in range(gfx.frames):
    surface = pygame.Surface((gfx.width, gfx.height))
    surface.set_colorkey((0, 0, 0))
    gfx.draw_frame(surface, i)
    surfaces.append(surface.convert())
  return surfaces

def _periodic_blit(source, destination):
  w, h = source.get_size()
  x, y = destination.get_size()
  for i in range(int(ceil(float(x) / w))):
    for j in range(int(ceil(float(y) / h))):
      destination.blit(source, (w * i, h * j))

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

class Monster2GFX(GFX):
  height = 10
  width = 10
  frames = 1

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    circle(surface, (0, 100, 255), (5, 5), 5)
    circle(surface, (100, 100, 100), (5, 5), 5, 2)

class TowerBubbleGFX(GFX):
  height = 25
  width = 25
  frames = 32

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
#    wid = self.width * (sin(n*pi/8) + 8) / 9.0
    layer = pygame.Surface((self.width, self.height))
    circle(layer, (255, 255, 255), (12, 12), 12)
    circle(layer, (0,   255, 0  ), (12, 12), 12, 1)
    wid = self.width
    hei = int(self.height * (cos(n*pi/16) + 4) / 5.0)
    surface.blit(pygame.transform.smoothscale(layer, (wid, hei)), (0, self.height - hei))
#    circle(surface, (12, 12), 12)
#    circle(surface, (0, 255, 0), (12, 12), 12, 1)

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
  width = 1024
  height = 768
  frames = 8
  compression = 20

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

  def draw_frame(self, surface, n):
    layer = pygame.Surface((16, 16))
    circle(layer, (120+100*sin(n*pi/self.frames*2), 0, 0), ((n%8)*2-8, (n%8)-8), 8)
    circle(layer, (120+100*sin(n*pi/self.frames*2), 0, 0), ((n%8)*2+8, (n%8)+8), 8)
    _periodic_blit(layer, surface)

  def draw_frame(self, surface, n):
    x, y = surface.get_size()
    xc = x / self.compression
    yc = y / self.compression
    layer = pygame.Surface((xc, yc))
    ary = numpy.zeros((xc, yc), dtype=numpy.int32)

    offset1 = 1 / (self.frames / 4.0)
    offset2 = pi/2.0
    for x in range(xc):
      for y in range(yc):
#        ary[x][y] = 1
        ary[x][y] = (sin((x+y+n*offset1)*offset2) + 1) * (cos((y*0.25+n*offset1)*offset2) + 1) * 8
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
    ary = numpy.zeros((self.width, self.height), dtype=numpy.int32)
    for x in range(self.width):
      for y in range(self.height):
        if y == 0 or y == self.height - 1:
          ary[x][y] = 255
        else:
          v = (sin((x/2+y+n/2.0)*pi/4) + 1) * 64 + 128
          if x > self.width - 50:
            ary[x][y] = min(255, (v + 3 * (x - self.width + 50)))
          else:
            ary[x][y] = min(255, v)
    pygame.surfarray.blit_array(surface, ary)
#    rect(surface, (0, 0, 205 + int(50 * abs(sin(n*pi/100)))), Rect(0, 0, self.width, self.height))

class CostBar(GFX):
  width = base_width = SCREEN_WIDTH
  height = 16
  frames = 1

  def __init__(self, args):
    self.scale = args[0]
    self.width = self.scale * self.base_width
    self.height = 16

  def draw_frame(self, surface, n):
    ary = numpy.zeros((self.width, self.height), dtype=numpy.int32)
    for x in range(self.width):
      for y in range(self.height):
        if y == 0 or y == self.height - 1:
          ary[x][y] = 255
        else:
          v = (sin((x/2+y+n/2.0)*pi/4) + 1) * 64 + 128
          if x > self.width - 50:
            ary[x][y] = min(255, (v + 3 * (x - self.width + 50)))
          else:
            ary[x][y] = min(255, v)
        ary[x][y] *= 256
    pygame.surfarray.blit_array(surface, ary)
#    rect(surface, (0, 0, 205 + int(50 * abs(sin(n*pi/100)))), Rect(0, 0, self.width, self.height))
