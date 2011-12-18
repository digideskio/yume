import pygame
import random
from math import *
from yume import *

class Tower(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)

  def move(self, x, y):
    self.rect.center = x, y

  def shoot(self, monster):
    Global.arena.projectiles.add(self.projectile(self, monster))


class Projectile(object):
  def __init__(self, origin, target):
    self.origin = origin
    self.target = target
    self.x, self.y = origin.rect.topleft

  def destroy(self):
    try:
      Global.arena.projectiles.remove(self)
    except:
      pass


class ProjectileBullet(Projectile):
  aoe = 7
  hits = 1
  speed = 2

  def __init__(self, origin, target):
    Projectile.__init__(self, origin, target)
    if hasattr(target, 'rect'):
      self.tx, self.ty = target.rect.center
      distance = sqrt((self.tx-self.x) ** 2 + (self.ty-self.y) ** 2) / self.speed
      self.tx += target.vector_x * target.speed * distance
      self.ty += target.vector_y * target.speed * distance
    else:
      self.tx, self.ty = target
    direction = atan2(self.ty - self.y, self.tx - self.x)
    self.dx = cos(direction) * self.speed
    self.dy = sin(direction) * self.speed
    self.damage = origin.damage
    self.distance = origin.range / self.speed
    self.traveled_distance = 0

  def draw(self, screen):
    pygame.draw.line(screen, (205, 100, 255), (self.x, self.y), (self.x+1, self.y+1))

  def update(self):
    self.x += self.dx
    self.y += self.dy
    self.traveled_distance += 1
    if self.traveled_distance >= self.distance:
      return self.destroy()
    monsters = list(Global.face.get_monsters_in_range(self.x, self.y, self.aoe))
    if monsters:
      i = 0
      for monster in monsters:
        monster.damage(self.damage, self.origin)
        i += 1
        if i >= self.hits:
          break
      self.destroy()

class TowerPrototype(Tower):
  imagefile = 'turret-1-1.png'
  cost = 28
  cooldown = 15
  cooldown_min = 4
  cooldown_step = 1
  range = 100
  damage = 4
  special_chance = 0.1
  projectile = ProjectileBullet

  def __init__(self):
    Tower.__init__(self)
    self.image = Global.images.load(self.imagefile)
    self.rect = self.image.get_rect()
    self.cooldown_tick = 0
    self.special_hits = 0
    self.phase = 0
    self.freq = 0

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1
    self.range = 100 + Global.face.mana

    if self.cooldown_tick <= 0:
      x, y = self.rect.center
      if self.special_hits <= 0 and random.random() <= self.special_chance:
        self.special_hits = random.randint(30,90)
        self.phase = random.random() * pi * 2
        self.freq = pi / random.randint(1, 30)
      if self.special_hits > 0:
        for i in range(3):
          self.phase += self.freq
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
