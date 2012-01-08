import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class Level(object):
  def __init__(self, startgene="", pools=1):
    self.gene = startgene

  def mutate(self, fittest=None):
    if fittest:
      self.gene = fittest.gene
    self.gene += random.sample('gatc', 1)[0]

  def single_mutation(self, gene):
    if gene and random.randint(0, 1):
      if random.randint(1,3) == 1:
        # append random trait
        return gene + random.sample('gatc', 1)[0]
      else:
        # swap one trait
        gene_l = list(gene)
        gene_l[random.randint(0, len(gene)-1)] = random.sample('gatc', 1)[0]
        return ''.join(gene_l)
    else:
      return gene

  def get_monsters(self):
    return list(self.single_mutation(self.gene) for _ in range(10))

  def make_grid(self, color):
    surface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    surface.set_colorkey((0, 0, 0))

    surface.lock()
    for i in range(40):
      x = i * 25
      pygame.draw.line(surface, color, (x, 0), (x, 27*25))
    for j in range(28):
      y = j * 25
      pygame.draw.line(surface, color, (0, y), (39*25, y))
#    for cell in self.cells:
#      pygame.draw.rect(surface, color, Rect(int(cell[0]*25), int(cell[1]*25), 25, 25))
    surface.unlock()
    return surface.convert_alpha()

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
        cells[(x, y)] = 1 if (c == 'o' or c == 'E') else 0
    self.cells = cells
    self.entry_points = entry_points


class Level1(Level):
  def __init__(self):
    self.startgene = ""
    self.pools = 1
    Level.__init__(self, self.startgene, self.pools)
    self.level = \
   """.................E.....................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      E.....................................E
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      .......................................
      ..........E...............E............"""
    self._convert_level(self.level)
