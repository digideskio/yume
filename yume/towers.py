import pygame
import random
from math import *
from pygame import Rect
from yume import *
from yume import gfx
from yume.resource import *
from yume.projectiles import *

class Tower(gfx.Drawable):
  gfx = None
  def __init__(self):
    gfx.Drawable.__init__(self)
    self.rect = Rect(0, 0, self.gfx.width, self.gfx.height)

  def update(self):
    pass

  def move(self, pos, gridpos):
    self.x, self.y = pos
    self.rect.topleft = pos
    self.gridpos = gridpos

  def shoot(self, monster):
    Global.arena.projectiles.append(self.projectile(self, monster))


class TowerBubble(Tower):
  graphic = gfx.TowerBubbleGFX
  transparent = True
#  gfx = gfx.TowerTurretGFX
  cost = 28
  adrenaline_cost = 5
  cooldown = 20
  cooldown_min = 10
  cooldown_step = 1
  range = 120
  damage = 4
  special_chance = 0.03  # overridden in yume.interface
  projectile = ProjectileBullet

  def __init__(self):
    Tower.__init__(self)
    self.cooldown_tick = 0
    self.special_hits = 0
    self.phase = 0
    self.freq = 0
    self.freq2 = 0
    self.animate = False

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    if self.animate:
      self.gfx.next_frame()
      if self.gfx.current_frame == 0:
        self.animate = False
    else:
      self.gfx.current_frame = 0

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1
#    self.range = 100 + Global.face.mana

    if self.cooldown_tick <= 0:
      x, y = self.rect.center
      if self.special_hits <= 0 and random.random() <= self.special_chance:
        monsters = list(Global.face.get_monsters_in_range(x, y, self.range))
        if len(monsters) >= 1:
          monster = monsters[0]
          x, y = monster.rect.center
          a, b = self.rect.center
          self.phase = atan2(y - b, x - a) - pi / 2
        else:
          self.phase = random.random() * pi * 2
        self.special_hits = random.randint(30,90)
        self.freq = pi / random.randint(1, 30)
        self.freq2 = pi * random.random() * 2
      if self.special_hits > 0:
        for i in range(3):
          self.phase += self.freq * sin(self.freq2 * self.special_hits)
          self.shoot((x + self.range * sin(self.phase), y + self.range * cos(self.phase)))
          self.animate = True
          self.special_hits -= 1
        self.cooldown_tick = 1
      else:
        monsters = list(Global.face.get_monsters_in_range(x, y, self.range))
        self.cooldown_tick = max(self.cooldown_min,
            self.cooldown - self.cooldown_step * len(monsters))
        if len(monsters) >= 1:
          monsters = random.sample(monsters, 1)
        for monster in monsters:
          self.shoot(monster)

  def shoot(self, monster):
    Tower.shoot(self, monster)
    self.animate = True
    self.gfx.current_frame = 2


class TowerLazor(Tower):
  graphic = gfx.TowerBubbleGFX
  transparent = True
  damage = 1
  range = 100
  cost = 10
  adrenaline_cost = 5

  def __init__(self):
    Tower.__init__(self)
    self.tick = 0
    self.target = None

  def update(self):
    x, y = self.rect.center
    self.tick += 1
    if self.tick >= 4:
      self.tick = 0
      if self.target and self.target.hp > 0 and self.range >= \
        Global.face.distance_between(x, y, self.target.x, self.target.y):
        self.target.damage(self.damage, self)
      else:
        monsters = Global.face.get_random_monster_in_range(x, y, self.range)
        if monsters:
          self.target = monsters[0]
        else:
          self.target = None

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()
    if self.target:
      pygame.draw.line(screen, (0, 255, 0), self.rect.center, (self.target.x, self.target.y), 1)


class TowerGuardian(Tower):
  graphic = gfx.TowerBubbleGFX
  projectile = ProjectileBullet
  transparent = True
  damage = 30
  range = 80
  cost = 10
  adrenaline_cost = 5
  cooldown = 30
  powerlevel = 5

  def __init__(self):
    Tower.__init__(self)
    self.powerlevel = 0
    self.target = None
    self.cooldown_tick = self.cooldown

  def update(self):
    x, y = self.rect.center
    self.powerlevel += 1
    if self.powerlevel >= self.cooldown:
      if self.target and self.target.hp > 0 and self.range >= \
        Global.face.distance_between(x, y, self.target.x, self.target.y):
          self.shoot(self.target)
      else:
        monsters = Global.face.get_random_monster_in_range(x, y, self.range)
        if monsters:
          self.target = monsters[0]
        else:
          self.target = None

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()
    if self.target:
      pygame.draw.line(screen, (100, 0, 0), self.rect.center, (self.target.x, self.target.y), 1)

  def shoot(self, target):
    self.damage = max(5, min(50, log(self.powerlevel - self.cooldown + 1, 1.1)))
    self.powerlevel = 0
    Tower.shoot(self, target)

class TowerBrain(Tower):
  graphic = gfx.TowerBrain
  transparent = True
  cost = 0
  adrenaline_cost = 50
  cooldown = 20

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    if random.randint(0,3) < 1:
      self.gfx.next_frame()

class TowerNode(Tower):
  graphic = gfx.TowerNode
  transparent = True
  cost = 0
  cooldown = 20
  adrenaline_cost = 30

  def update(self):
    pass
