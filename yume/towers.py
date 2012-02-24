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
    Global.arena.shots += 1
    Global.arena.projectiles.append(self.projectile(self, monster))

  def hit(self, monster, bullet):
    Global.arena.hits += 1
    monster.damage(bullet.damage, self)


class TowerBubble(Tower):
  graphic = gfx.TowerBubbleGFX
  transparent = True
#  gfx = gfx.TowerTurretGFX
  cost = 22
  adrenaline_cost = 5
  cooldown = 14 # has a variable cooldown
  cooldown_min = 14
  cooldown_step = 2
  range = 130
  damage = 8
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
    self.has_just_been_built = False

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
      if self.special_hits <= 0 and random.random() <= self.special_chance \
          or self.has_just_been_built:
        self.has_just_been_built = False
        monsters = list(Global.face.get_monsters_in_range(x, y, self.range))
        if len(monsters) >= 1:
          monster = monsters[0]
          x, y = monster.rect.center
          a, b = self.rect.center
#          self.phase = atan2(x - a, y - b)
          self.phase = atan2(y - b, x - a) + pi / 2
        else:
          self.phase = random.random() * pi * 2
        #self.special_hits = random.randint(30,90)
        self.special_hits = random.randint(80,180)
        self.freq = pi / random.randint(1, 30)
        self.freq2 = pi * random.random() * 2 + pi
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
  graphic = gfx.TowerLazorGFX
  transparent = True
  damage = 2
  range = 100
  cost = 16
  adrenaline_cost = 5

  def __init__(self):
    Tower.__init__(self)
    self.tick = 0
    self.phase = 0
    self.target = None

  def update(self):
    x, y = self.rect.center
    self.tick += 1
    if self.tick < 3:
      return

    self.tick = 0
    targets = list(Global.face.get_monsters_in_line(x, y, x + cos(self.phase) * self.range, y + sin(self.phase) * self.range, 10))
    if self.target and self.target.hp > 0 and self.range >= \
      Global.face.distance_between(x, y, self.target.x, self.target.y) and \
      (self.target in targets or not targets):
        # angle is the angle between the tower and the monster
        # phase is the orientation of the laser
        angle = atan2(self.target.y - y, self.target.x - x)
        diff = (self.phase - angle + pi) % (2 * pi) - pi
        self.phase = angle if abs(diff) < 0.04 else self.phase - max(-0.1, min(0.1, diff))
        for mob in targets:
          mob.damage(self.damage, self, ignore_shield=True)
    else:
      monsters = Global.face.get_random_monster_in_range(x, y, self.range)
      if monsters:
        self.target = monsters[0]
      else:
        self.target = None

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
#    self.gfx.next_frame()
    if self.target:
      x, y = self.rect.center
      x += cos(self.phase) * self.range
      y += sin(self.phase) * self.range
      pygame.draw.line(screen, (0, 255, 0), self.rect.center, (x, y), 1)


class TowerVirus(Tower):
  graphic = gfx.TowerVirusGFX
  cost = 52
  adrenaline_cost = 8
  transparent = True
  range = 200
  damage = 0
  cooldown = 42
  projectile = ProjectileVirus

  def __init__(self):
    Tower.__init__(self)
    self.cooldown_tick = 0

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1
#    self.range = 100 + Global.face.mana

    if self.cooldown_tick <= 0:
      x, y = self.rect.center
      monsters = list(Global.face.get_monsters_in_range(x, y, self.range))
      self.cooldown_tick = self.cooldown
      if len(monsters) >= 1:
        monsters = random.sample(monsters, 1)
      for monster in monsters:
        self.shoot(monster)

  def hit(self, monster, bullet):
    Tower.hit(self, monster, bullet)
    monster.poison(strength=4, duration=10, dealer=self)


class TowerGuardian(Tower):
  graphic = gfx.TowerGuardianGFX
  projectile = ProjectileGuardianBullet
  transparent = True
  damage = 120.0
  min_damage = 4
  range = 60
  cost = 40
  adrenaline_cost = 8
  cooldown = 30
  powerlevel = 0
  powerlevel_recharge_rate = 1
  max_powerlevel = 500.0

  def __init__(self):
    Tower.__init__(self)
    self.target = None
    self.base_damage = self.damage
    self.cooldown_tick = self.cooldown

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1
    if self.powerlevel < self.max_powerlevel:
      self.powerlevel += self.powerlevel_recharge_rate

    if self.cooldown_tick <= 0:
      x, y = self.rect.center
      if self.target and self.target.hp > 0 and self.range >= \
        Global.face.distance_between(x, y, self.target.x, self.target.y):
          self.shoot(self.target)
          self.cooldown_tick = self.cooldown
      else:
        monsters = Global.face.get_random_monster_in_range(x, y, self.range)
        if monsters:
          self.target = monsters[0]
        else:
          self.target = None

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()
#    if self.target:
#      pygame.draw.line(screen, (100, 0, 0), self.rect.center,
#          (self.target.x, self.target.y), 1)

    wid = max(0, min(self.gfx.width-2, self.gfx.width * self.powerlevel / self.max_powerlevel))
    pygame.draw.line(screen, (0, 255, 0), (self.x, self.y + self.gfx.height / 2), (self.x + wid, self.y + self.gfx.height / 2), 2)

  def shoot(self, target):
    self.damage = min(self.base_damage, max(self.min_damage, sqrt(self.powerlevel) + self.base_damage / (1 + self.max_powerlevel - self.powerlevel)))
    #print(self.damage)
    self.powerlevel *= 0.6
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
