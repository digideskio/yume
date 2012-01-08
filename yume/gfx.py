import pygame
import numpy
import time
from sys import stderr
from math import *
from pygame import Rect
from pygame.draw import *
from yume import *
from yume.lib import cached_method

#=============================================================================
#== Access functions

#_gfx_cache = {}

class Drawable(object):
  graphic = None
  transparent = False
  def __init__(self):
    self.x, self.y = 0, 0
    self.rect = Rect(0, 0, 1, 1)
    if self.graphic:
      self.gfx = get_gfx(self.graphic, (1, 1), self.transparent)
      self.rect = Rect(0, 0, self.gfx.width, self.gfx.height)

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()

class GFX(object):
  frames = 1
  current_frame = -1
  transparent = False

  def __init__(self):
    self.set_frame(0)

  def next_frame(self):
    if self.frames > 1:
      self.current_frame = (self.current_frame + 1) % self.frames
      self.surface = get_surface(self.__class__, self.current_frame,
          hash(self.__class__.__name__))

  def set_frame(self, n):
    if n != self.current_frame:
      self.current_frame = n % self.frames
      self.surface = get_surface(self.__class__, self.current_frame,
          hash(self.__class__.__name__))

@cached_method
def get_surface(*args):
  cls = args[0]
  transparency = cls.transparent
  surface = pygame.Surface((cls.width, cls.height))
  if transparency:
    surface.set_colorkey((0, 0, 0))
  cls.draw_frame(surface, args[1])
  if transparency:
    return surface.convert_alpha()
  return surface.convert()

def get_gfx(name, args, transparency=False):
  return name(args)

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
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
    line(surface, (205, 100, 255), (2, 2), self.foo[n])

class Bubble(GFX):
  height = 5
  width = 5
  frames = 1
#  foo = [(4, 2), (2, 4), (0, 2), (2, 0)]

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
    circle(surface, (255, 255, 255), (2, 2), 2)
#    line(surface, (205, 100, 255), (2, 2), self.foo[n])

class MonsterGFX(GFX):
  height = 10
  width = 10
  frames = 1
  transparent = True

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
    circle(surface, (255, 0, 0), (5, 5), 5)
    circle(surface, (100, 100, 100), (5, 5), 5, 2)

class Monster2GFX(GFX):
  height = 10
  width = 10
  frames = 1

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
    circle(surface, (0, 100, 255), (5, 5), 5)
    circle(surface, (100, 100, 100), (5, 5), 5, 2)

class TowerBubbleGFX(GFX):
  height = 24
  width = 24
  frames = 32
  transparent = True

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
#    wid = self.width * (sin(n*pi/8) + 8) / 9.0
    layer = pygame.Surface((self.width, self.height))
    circle(layer, (150, 150, 255), (12, 12), 12)
    circle(layer, (100, 100, 100), (12, 12), 12, 1)
    wid = self.width
    hei = int(self.height * (cos(n*pi/16) + 4) / 5.0)
    surface.blit(pygame.transform.smoothscale(layer, (wid, hei)), (0, self.height - hei))
#    circle(surface, (12, 12), 12)
#    circle(surface, (0, 255, 0), (12, 12), 12, 1)

class TowerLazorGFX(GFX):
  height = 24
  width = 24
  frames = 1
  transparent = True

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args

  @classmethod
  def draw_frame(self, surface, n):
#    wid = self.width * (sin(n*pi/8) + 8) / 9.0
    layer = pygame.Surface((self.width, self.height))
    circle(layer, (40, 40, 40), (12, 12), 12)
    circle(layer, (100, 100, 100), (12, 12), 12, 1)
    wid = self.width
    hei = int(self.height * (cos(n*pi/16) + 4) / 5.0)
    surface.blit(pygame.transform.smoothscale(layer, (wid, hei)), (0, self.height - hei))
#    circle(surface, (12, 12), 12)
#    circle(surface, (0, 255, 0), (12, 12), 12, 1)

class TowerBrain(GFX):
  height = 24
  width = 24
  frames = 8
  transparent = True

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args
    self.recoil = 0
#    self.scale, self.rotation, self.recoil = args
    self.height = int(self.height * self.scale)
    self.width = int(self.width * self.scale)

  @classmethod
  def draw_frame(self, surface, n):
    layer = pygame.Surface((self.width * 4, self.height * 4))
    circle(layer, (1 + (n % 2) * 154, ((n % 4) < 2) * 155, (n < 4) * 155), (48, 48), 48)
    surface.blit(pygame.transform.smoothscale(layer, (self.width, self.height)), (0, 0))
#    circle(surface, (255, 0, 0), (12, 12), 12)

class TowerNode(GFX):
  height = 24
  width = 24
  frames = 64
  transparent = True

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, self.rotation = args
    self.recoil = 0
#    self.scale, self.rotation, self.recoil = args
    self.height = int(self.height * self.scale)
    self.width = int(self.width * self.scale)

  @classmethod
  def draw_frame(self, surface, n):
    layer = pygame.Surface((self.width*4, self.height*4))
    color = 225 + sin(n*2*pi/self.frames) * 30
    circle(layer, (250, 250, 250), (48, 48), 20)
    circle(layer, (color, color, color), (48, 48), 12)
#    circle(layer, (255, 255, 200), (12, 12), 4)
#    wid = int(self.width * (cos(n*2*pi/self.frames) + 4) / 5.0)
#    hei = int(self.height * (cos(n*2*pi/self.frames) + 4) / 5.0)
    surface.blit(pygame.transform.smoothscale(layer, (self.width, self.height)), (0, 0))

class TestBackground(GFX):
  width = SCREEN_WIDTH
  height = SCREEN_HEIGHT
  frames = 1

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, _ = args

  @classmethod
  def draw_frame(self, surface, n):
    surface.fill((0, 0, 0))

class Background(GFX):
  width = SCREEN_WIDTH
  height = SCREEN_HEIGHT
  frames = 16
  compression = 20

  def __init__(self, args):
    GFX.__init__(self)
    self.scale, _ = args
    self.height = int(self.height * self.scale)
    self.width = int(self.width * self.scale)

  @classmethod
  def draw_frame(self, surface, n):
    for j in range(20):
      points = []
      for i in range(120):
        points.append(((0 if i % 2 else 10) + j * 40, 5*i+n))
      for i in range(120):
        points.append(((0 if i % 2 else 10) + j * 40, 600-5*i+n+j))
      polygon(surface, (155, 0, 0), points)

  @classmethod
  def draw_frame(self, surface, n):
    layer = pygame.Surface((16, 16))
    circle(layer, (120+100*sin(n*pi/self.frames*2), 0, 0), ((n%8)*2-8, (n%8)-8), 8)
    circle(layer, (120+100*sin(n*pi/self.frames*2), 0, 0), ((n%8)*2+8, (n%8)+8), 8)
    _periodic_blit(layer, surface)

  @classmethod
  def draw_frame2(self, surface, n):
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

  @classmethod
  def draw_frame(self, surface, n):
    self.draw_frame2(surface,n)
    layer = pygame.Surface((16, 32))
    layer.set_colorkey((0, 0, 0))
    points = []
    points.append((0, -32+n*2))
    points.append((8, -16+n*2))
    points.append((0, n*2))
    points.append((8, 16+n*2))
    points.append((0, 32+n*2))
    points.append((2, 32+n*2))
    points.append((10, 16+n*2))
    points.append((2, n*2))
    points.append((10, -16+n*2))
    points.append((2, -32+n*2))
#    lines(layer, (155, 0, 0), True, points)
    polygon(layer, (50, 50, 0), points)
    _periodic_blit(layer, surface)

class ManaBar(GFX):
  width = base_width = SCREEN_WIDTH - 40
  height = 16
  frames = 1

  def __init__(self, args):
    GFX.__init__(self)
    self.scale = args[0]
    self.width = self.scale * self.base_width
    self.height = 16

  @classmethod
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
  width = base_width = SCREEN_WIDTH - 40
  height = 16
  frames = 1

  def __init__(self, args):
    GFX.__init__(self)
    self.scale = args[0]
    self.width = self.scale * self.base_width
    self.height = 16

  @classmethod
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

class AdrenalineBar(GFX):
  width = base_width = SCREEN_WIDTH - 40
  height = 6
  frames = 1
#  frames = 16

  def __init__(self, args):
    GFX.__init__(self)
    self.scale = args[0]
    self.width = self.scale * self.base_width
#    self.height = 16

  @classmethod
  def draw_frame(self, surface, n):
    ary = numpy.zeros((self.width, self.height), dtype=numpy.int32)
    for x in range(self.width):
      for y in range(self.height):
        if y == 0 or y == self.height - 1:
          ary[x][y] = 255
        else:
          v = (sin((x/2+y+n/2.0)*pi/4) + 1) * 64 + 128
          if x > self.width - 50:
            ary[x][y] = min(200, (v + 3 * (x - self.width + 50)))
          else:
            ary[x][y] = min(200, v)
        ary[x][y] *= 256 * 256
#        ary[x][y] *= 16776960
    pygame.surfarray.blit_array(surface, ary)

class AdrenalineCostBar(GFX):
  width = base_width = SCREEN_WIDTH - 40
  height = 6
  frames = 50

  def __init__(self, args):
    GFX.__init__(self)
    self.scale = args[0]
    self.width = self.scale * self.base_width

  @classmethod
  def draw_frame(self, surface, n):
    rect(surface, (170 , 170, 30), Rect(0, 0, self.width, self.height))

class UIGFX(GFX):
  width = 100
  height = SCREEN_HEIGHT
  frames = 1

  def __init__(self, args):
    GFX.__init__(self)
    self.scale = args[0]

  @classmethod
  def draw_frame(self, surface, n):
    rect(surface, (100, 100, 100), Rect(0, 0, self.width, self.height))
    rect(surface, (200, 200, 200), Rect(10, 20, self.width-20, 300))
