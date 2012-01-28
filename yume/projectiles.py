import pygame
import random
from math import *
from yume import *
from yume import gfx
from yume.gfx import get_gfx
from yume.resource import *
from pygame import Rect

class Projectile(gfx.Drawable):
  def __init__(self, origin, target):
    gfx.Drawable.__init__(self)
    self.origin = origin
    self.target = target
    self.x, self.y = origin.rect.center

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x, self.y))
    self.gfx.next_frame()

  def destroy(self):
    try:
      Global.arena.projectiles.remove(self)
    except:
      pass

class ProjectileDumb(Projectile):
  aoe = 7
  hits = 1
  def __init__(self, origin, target):
    Projectile.__init__(self, origin, target)
    if hasattr(target, 'rect'):
      self.tx, self.ty = target.rect.center
    else:
      self.tx, self.ty = target
    direction = atan2(self.ty - self.y, self.tx - self.x)
    self.dx = cos(direction) * self.speed
    self.dy = sin(direction) * self.speed
    self.damage = origin.damage
    self.distance = origin.range / self.speed
    self.traveled_distance = random.randint(0, 5)

  def update(self):
    self.x += self.dx
    self.y += self.dy
    self.traveled_distance += 1
    if self.traveled_distance >= self.distance:
      return self.destroy()
    area = Rect(self.x - self.aoe, self.y - self.aoe, 2 * self.aoe, 2 * self.aoe)
#    area = Rect(self.x-self.aoe/2, self.y-self.aoe/2, self.aoe, self.aoe)
    monsters = list(Global.face.get_monsters_in_rect(area))
    if monsters:
      i = 0
      for monster in monsters:
        self.origin.hit(monster, self)
        i += 1
        if i >= self.hits:
          break
      self.destroy()

class ProjectileBullet(ProjectileDumb):
  aoe = 7
  hits = 1
  speed = 3
  graphic = gfx.Bubble

  def __init__(self, origin, target):
    ProjectileDumb.__init__(self, origin, target)
    if hasattr(target, 'rect'):
      self.tx, self.ty = target.rect.center
      distance = sqrt((self.tx-self.x) ** 2 + (self.ty-self.y) ** 2) / self.speed
      self.tx += target.vector_x * target.speed * distance
      self.ty += target.vector_y * target.speed * distance
    else:
      self.tx, self.ty = target
    direction = atan2(self.ty - self.y, self.tx - self.x)
#    self.gfx = get_gfx(gfx.B, (1, 1))
    self.dx = cos(direction) * self.speed
    self.dy = sin(direction) * self.speed
    self.damage = origin.damage
    self.distance = origin.range / self.speed
    self.traveled_distance = random.randint(0, 5)

class ProjectileGuardianBullet(ProjectileBullet):
  graphic = gfx.GuardianBullet
  speed = 4
  aoe = 10


class ProjectileVirus(ProjectileDumb):
  speed = 2
  graphic = gfx.Virus
