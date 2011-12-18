import pygame
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
    self.x, self.y = origin.rect.center

  def destroy(self):
    try:
      Global.arena.projectiles.remove(self)
    except:
      pass


class ProjectileBullet(Projectile):
  aoe = 5
  speed = 2

  def __init__(self, origin, target):
    Projectile.__init__(self, origin, target)
    self.tx, self.ty = target.rect.center
    direction = atan2(self.ty - self.y, self.tx - self.x)
    self.dx = cos(direction) * self.speed
    self.dy = sin(direction) * self.speed
    self.damage = origin.damage
    self.distance = origin.range / self.speed
    self.traveled_distance = 0

  def draw(self, screen):
    pygame.draw.line(screen, (255, 100, 255), (self.x, self.y), (self.x+1, self.y+1))

  def update(self):
    self.x += self.dx
    self.y += self.dy
    self.traveled_distance += 1
    if self.traveled_distance >= self.distance:
      return self.destroy()
    monsters = list(Global.face.get_monsters_in_range(self.x, self.y, self.aoe))
    if monsters:
      for monster in monsters:
        monster.damage(self.damage, self.origin)
      self.destroy()

class TowerPrototype(Tower):
  imagefile = 'turret-1-1.png'
  cost = 30
  cooldown = 5
  range = 100
  damage = 2
  projectile = ProjectileBullet

  def __init__(self):
    Tower.__init__(self)
    self.image = Global.images.load(self.imagefile)
    self.rect = self.image.get_rect()
    self.cooldown_tick = 0

  def update(self):
    if self.cooldown_tick > 0:
      self.cooldown_tick -= 1

    if self.cooldown_tick <= 0:
      self.cooldown_tick = self.cooldown
      x, y = self.rect.center
      for monster in Global.face.get_random_monster_in_range(x, y, self.range):
        self.shoot(monster)
