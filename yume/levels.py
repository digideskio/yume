import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class MetaMonster(object):
  def __init__(self, gene=""):
    self.gene, self.fitness = gene, 1

  def clone(self):
    return MetaMonster(self.gene)


class Pool(object):
  def __init__(self, startgene, startpopulation, boss=False, creeps=None):
    self.startgene = startgene
    self.startpopulation = startpopulation
    self.boss = boss
    self.monsters_left = startpopulation
    if creeps == None:
      self.creeps = [MetaMonster(startgene) for _ in range(startpopulation)]
    else:
      self.creeps = creeps

  def clone(self):
    return Pool(self.startgene, self.startpopulation, self.boss, creeps=list(self.creeps))

  def get_next(self):
    return self.creeps.pop()


class Level(object):
  def __init__(self, startgene=""):
    self.boss_freq = 4
    self.level_number = 0
    self.genepools = []
    self.genepools.append(Pool(startgene + "B", 3, boss=True))
    self.genepools.append(Pool(startgene, 6))
    self.genepools.append(Pool(startgene, 6))
    self.genepools.append(Pool(startgene, 6))
    self.sampling_method = self.sm_stochastic_universal_sampling

  #def sm_fittest(self):
    #pool = list(self.dead_monsters)
    #pool.sort(key=lambda mob: -mob.fitness)
    #fittest = pool[0].gene
    #mutated = fittest + random.sample(Monster.traits, 1)[0]
    #mutated = self.single_mutation(mutated)
    #self.genepool = [mutated] * self.individuals

  def sm_stochastic_universal_sampling(self, pool):
    pool.sort(key=lambda meta: -meta.fitness)
    total_fitness = sum(meta.fitness for meta in pool)
    step = 1.0 / len(pool)
    new_pool = []

    pos = random.random() * step
    accumulated_fitness = pool[0].fitness
    index = 0
    for i in range(len(pool)):
      while pos > accumulated_fitness:
        accumulated_fitness += pool[index].fitness
        index += 1
      meta = pool[index].clone()
      new_pool.append(meta)
    return new_pool

  def mutate(self):
    if self.level_number % self.boss_freq == 0:
      self.genepools[0].creeps = self.sampling_method(self.genepools[0].creeps)
      for meta in self.genepools[0].creeps:
        for _ in range(8):
          meta.gene += random.sample(Monster.traits, 1)[0]
        for _ in range(4):
          meta.gene = self.single_mutation(meta.gene)
    else:
      for i in range(1, len(self.genepools)):
        self.genepools[i].creeps = self.sampling_method(self.genepools[i].creeps)
        for meta in self.genepools[i].creeps:
          meta.gene += random.sample(Monster.traits, 1)[0]
          meta.gene = self.single_mutation(meta.gene)
          meta.gene = self.single_mutation(meta.gene)
          meta.gene = self.single_mutation(meta.gene)

  def single_mutation(self, gene):
    if random.randint(0, 2):
      if gene and random.randint(1, 4) < 4:
        # swap one trait
        gene_l = list(gene)
        random_pos = random.randint(0, len(gene)-1)
        if gene_l[random_pos] != 'B':
          gene_l[random_pos] = random.sample(Monster.traits, 1)[0]
        return ''.join(gene_l)
      else:
        # append random trait
        return gene + random.sample(Monster.traits, 1)[0]
    return gene

  def get_monsters_of_next_level(self):
    self.level_number += 1
    self.mutate()
    if self.level_number % self.boss_freq == 0:
      return [self.genepools[0].clone()]
    else:
      return [pool.clone() for pool in self.genepools[1:]]

  clone_pools = get_monsters_of_next_level

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
    Level.__init__(self, self.startgene)
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
