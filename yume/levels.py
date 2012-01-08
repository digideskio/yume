import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class Level(object):
  def __init__(self, startgene="", pools=1):
    self.individuals = 10
    self.genepool = [startgene] * self.individuals
    self.sampling_method = self.sm_stochastic_universal_sampling

  def sm_fittest(self):
    pool = list(self.dead_monsters)
    pool.sort(key=lambda mob: -mob.fitness)
    fittest = pool[0].gene
    mutated = fittest + random.sample(Monster.traits, 1)[0]
    mutated = self.single_mutation(mutated)
    self.genepool = [mutated] * self.individuals

  def sm_stochastic_universal_sampling(self):
    pool = list(self.dead_monsters)
    pool.sort(key=lambda mob: -mob.fitness)
    total_fitness = sum(mob.fitness for mob in self.dead_monsters)
    step = 1.0 / self.individuals
    self.genepool = []

    pos = random.random() * step
    accumulated_fitness = pool[0].fitness
    index = 0
    for i in range(self.individuals):
      while pos > accumulated_fitness:
        accumulated_fitness += pool[index].fitness
        index += 1
      gene = pool[index].gene + random.sample(Monster.traits, 1)[0]
      gene = self.single_mutation(gene)
      self.genepool.append(gene)

  def mutate(self, dead_monsters):
    self.dead_monsters = dead_monsters
    self.sampling_method()

  def single_mutation(self, gene):
    if gene and random.randint(0, 1):
      if random.randint(1,3) == 1:
        # append random trait
        return gene + random.sample(Monster.traits, 1)[0]
      else:
        # swap one trait
        gene_l = list(gene)
        gene_l[random.randint(0, len(gene)-1)] = random.sample(Monster.traits, 1)[0]
        return ''.join(gene_l)
    else:
      return gene

  def get_monsters(self):
    self.last_monsters = tuple(self.genepool)
#    self.last_monsters = tuple(self.single_mutation(gene) for gene in self.genepool)
    return list(self.last_monsters)

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
