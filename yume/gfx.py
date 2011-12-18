import pygame
from math import *
from pygame import Rect
from pygame.draw import *
from yume import *

class GFX(object):
  frames = 1
  current_frame = 0

  def next_frame(self):
    self.current_frame = (self.current_frame + 1) % len(self.surfaces)
    self.surface = self.surfaces[self.current_frame]

def draw_gfx(cls, args):
  gfx = cls(args)
  surfaces = []
  for i in range(gfx.frames):
    surface = pygame.Surface((gfx.width, gfx.height))
    surface.set_colorkey((0, 0, 0))
    gfx.draw_frame(surface, i)
    surfaces.append(surface)
  gfx.surfaces = surfaces
  gfx.surface = surfaces[gfx.current_frame]
  return gfx

class Bullet(GFX):
  height = 5
  width = 5
  frames = 4
  foo = [(4, 2), (2, 4), (0, 2), (2, 0)]

  def __init__(self, args):
    self.scale, self.rotation = args

  def draw_frame(self, surface, n):
    line(surface, (205, 100, 255), (2, 2), self.foo[n])


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

