import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class Level(object):
  def __init__(self, startgene="", pools=1):
    self.gene = startgene

  def mutate(self):
    self.gene += random.sample('abc', 1)[0]

  def get_monsters(self):
    return list(self.gene for _ in range(10))

  def make_grid(self, color):
    surface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    surface.set_colorkey((0, 0, 0))

    surface.lock()
    surface.fill((0, 0, 0))
    for i in range(40):
      x = i * 25
      pygame.draw.line(surface, color, (x, 0), (x, 26*25))
    for j in range(27):
      y = j * 25
      pygame.draw.line(surface, color, (0, y), (39*25, y))
    for cell in self.cells:
      pygame.draw.rect(surface, color, Rect(int(cell[0]*25), int(cell[1]*25), 25, 25))
    surface.unlock()
    return surface.convert()

  def _convert_level(self, string):
    cells = {}
    entry_points = []
    for y, line in enumerate(string.split("\n")):
      line = line.strip()
      last_entry_point = -1
      for i in range(line.count('E')):
        last_entry_point = line.find('E', last_entry_point + 1)
        entry_points.append((last_entry_point, y))
      for x, c in enumerate(line):
        if c == 'o' or c == 'E':
          cells[(x, y)] = 1
    self.cells = cells
    self.entry_points = entry_points


class Level1(Level):
  def __init__(self):
    self.startgene = ""
    self.pools = 1
    Level.__init__(self, self.startgene, self.pools)
    self.level = \
   """.............ooooEoooo.................
      ..............ooooooo..................
      ................ooo....................
      .................oo....................
      .................oo....................
      ..................o....................
      ..................oo...................
      ...................o...................
      ..................ooo..................
      .................oooo..................
      ...............oooooooooo..............
      oo..........oooooooooooooooo.........oo
      ooooooooooooooooooooooooooooo......oooo
      Eooooooooooo.oooooooooooooooooooooooooE
      oooo..........oooooooooooo....ooooooooo
      oo..............oooooooo.............oo
      ..................ooooo................
      ...................oooo................
      ...................ooo.................
      ..................ooo..................
      ..................ooo..................
      ..................ooo..................
      ...................ooo.................
      ....................ooo................
      ...................oooo................
      .................ooooooo...............
      ................ooooEoooo.............."""

    self.level = \
   """ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      oooooooooooooooooooooooooo.....oooooooo
      oooooooooooooooooooooooo.....E...oooooo
      ooooooooooooooooooooooooo......oooooooo
      oooooooooooooooooooooooo.oooooooooooooo
      ooooooooooooooooooooooo.ooooooooooooooo
      oooooooooooooooooooooo.oooooooooooooooo
      oooooooooooooooooooo...oooooooooooooooo
      ooooooooooooooooooo...ooooooooooooooooo
      oooooooooooooooooo...oooooooooooooooooo
      oooooooooooooooooo.oooooooooooooooooooo
      ooooooooooooooooo.ooooooooooooooooooooo
      oooooooooooooooo.oooooooooooooooooooooo
      oooooooooo......ooooooooooooooooooooooo
      oooooooo...E.....oooooooooooooooooooooo
      oooooooooo.....oooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo
      ooooooooooooooooooooooooooooooooooooooo"""
    self._convert_level(self.level)
