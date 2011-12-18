import pygame
from math import *
from yume import *

class Tower(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)

  def move(self, x, y):
    self.rect.center = x, y

class TowerPrototype(Tower):
  imagefile = 'turret-1-1.png'
  cost = 30

  def __init__(self):
    Tower.__init__(self)
    self.image = Global.images.load(self.imagefile)
    self.rect = self.image.get_rect()

  def update(self):
    for monster in Global.yume.interface.arena.level.mobrenderer:
      if self.distance(*monster.rect.center) < 50:
        monster.damage(1, self)

  def distance(self, x1, y1):
    x2, y2 = self.rect.center
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
