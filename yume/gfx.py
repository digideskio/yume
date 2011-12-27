import pygame
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

class ManaBar(GFX):
  width = base_width = SCREEN_WIDTH
  height = 16
  frames = 100

  def __init__(self, args):
    self.scale = args[0]
    self.width = self.scale * self.base_width
    self.height = 16

  def draw_frame(self, surface, n):
    rect(surface, (0, 0, 205 + int(50 * abs(sin(n*pi/100)))), Rect(0, 0, self.width, self.height))

