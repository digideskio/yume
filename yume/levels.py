import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class Wave(object):
  def __init__(self, monsters, mps, delay):
    self.monsters = monsters
    self.mps = mps  # monsters per second
    self.delay = delay

  def engage(self):
    add = lambda x, y: x + y
    self.monster_queue = reduce(add,
        [[cls] * n for cls, n in self.monsters.items()])
    random.shuffle(self.monster_queue)
    self.monster_delay = 1 / float(self.mps)
    self.monster_tick = 0

class Level(object):
  def __init__(self):
    self.waves = deque()
    self.waypoints = [(0, 0)]
    self.delay = 1
    self.last_update = 0

  def initialize(self):
    self.mobrenderer = pygame.sprite.RenderPlain([])
    self.cells = [[1] * CELLS_X for _ in range(CELLS_Y)]
    self.remove_wave = 0
    self.active_waves = set()
    self.surface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    self.mobsurface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    self.mobsurface.set_colorkey((0, 0, 0))
    self.mobsurface = self.mobsurface.convert()

    def mult(pair):
      return (pair[0] * 25, pair[1] * 25)

    self.waypoints_scaled = map(mult, self.waypoints)

    t1 = time.time()
    self.surface.lock()
    self.surface.fill((0, 0, 0))
    for wp in self.waypoints:
      wp_m = (wp[0] * CELL_WIDTH + 1, wp[1] * CELL_WIDTH + 1)
      pygame.draw.circle(self.surface, (0, 155, 0), wp_m, 12, 0)
      pygame.draw.circle(self.surface, (0, 0, 0), wp_m, 11, 0)
    pygame.draw.lines(self.surface, (0, 155, 0), False, self.waypoints_scaled, 24)
    pygame.draw.lines(self.surface, (0, 0, 0), False, self.waypoints_scaled, 22)
    self.surface.unlock()
    self.surface = self.surface.convert()

  def update(self):
    if self.last_update:
      dt = time.time() - self.last_update

      for mob in list(self.mobrenderer):
        if mob.hp <= 0:
          self.mobrenderer.remove(mob)
          if mob.killer:
            Global.yume.interface.mana += mob.worth

      self.mobrenderer.update()

      for wave in list(self.active_waves):
        if wave.monster_queue:
          wave.monster_tick -= dt
          if wave.monster_tick < 0:
            monster = wave.monster_queue.pop()
            self.spawn(monster)
            wave.monster_tick = wave.monster_delay 

      self.delay -= dt
      if self.waves and self.delay < 0:
        wave = self.waves.popleft()
        wave.engage()
        self.active_waves.add(wave)
        self.delay = wave.delay

    self.last_update = time.time()

  def spawn(self, monster):
    mon = monster()
    mon.x, mon.y = self.waypoints_scaled[0]
    mon.waypoints = self.waypoints_scaled
    self.mobrenderer.add(mon)

  def draw(self, screen):
    screen.blit(self.surface, (ARENA_LEFT_POS, ARENA_TOP_POS))
    self.mobsurface.fill((0, 0, 0))
    self.mobrenderer.draw(self.mobsurface)
    screen.blit(self.mobsurface, (ARENA_LEFT_POS, ARENA_TOP_POS))

  def draw_above(self, screen):
    pass

class LevelInvocation(Level):
  def __init__(self):
    Level.__init__(self)
    self.waypoints = [(10, 0), (10, 4), (3, 4), (3, 8), (12, 8), (12, 16),
        (6, 16), (6, 21), (18, 21), (18, 8), (32, 8)]
    self.waves = deque()
    self.waves.append(Wave({Lame: 5}, mps=1, delay=3))
    self.waves.append(Wave({Lame: 10}, mps=10, delay=2))
    self.waves.append(Wave({Lame: 30}, mps=60, delay=2))
