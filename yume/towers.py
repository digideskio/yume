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
  cooldown = 20
  cooldown_min = 10
  cooldown_step = 1
  range = 100
  damage = 4
  special_chance = 0.03
  projectile = ProjectileBullet

  def __init__(self):
    Tower.__init__(self)
    self.cooldown_tick = 0
    self.special_hits = 0
    self.phase = 0
    self.freq = 0
    self.freq2 = 0

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1
    self.range = 100 + Global.face.mana

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

class TowerBrain(Tower):
  graphic = gfx.TowerBrain
  transparent = True
  cost = 200
  cooldown = 20

  def update(self):
    pass

class TowerNode(Tower):
  graphic = gfx.TowerNode
  transparent = True
  cost = 2
  cooldown = 20

  def update(self):
    pass
