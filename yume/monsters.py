import pygame
import random
from math import *
from yume import *

class Monster(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.waypoint_index = 1
    self.waypoints = [(0, 0)]
    self.hp = 10
    self.worth = 4
    self.calc_vector = True
    self.vector_y = 0
    self.vector_x = 0
    self.speed = 1
    self.killer = None

  def walk(self):
    if self.hp <= 0:
      return
    try:
      waypoint = self.waypoints[self.waypoint_index]
    except:
      Global.yume.interface.crash()
      self.die()
    else:
      x = waypoint[0] - self.x
      y = waypoint[1] - self.y
      if self.calc_vector:
        rotation = atan2(y, x)
        self.vector_x = cos(rotation)
        self.vector_y = sin(rotation)
        self.calc_vector = False
      distance = sqrt(x*x+y*y)
      if distance < 10:
        self.waypoint_index += 1
        self.calc_vector = True
      else:
        self.t += pi / 20
        self.x += self.vector_x * self.speed
        self.y += self.vector_y * self.speed

    self.rect.center = (self.x, self.y)

  def die(self):
    self.hp = 0

  def damage(self, damage, dealer):
    if self.hp > 0:
      self.hp -= damage
      if self.hp <= 0:
        self.killer = dealer

class Lame(Monster):
  def __init__(self):
    Monster.__init__(self)
    self.image = Global.images.load('enemy-1-pain.png')
    self.rect = self.image.get_rect()
    self.x = random.randint(100, 800)
    self.y = random.randint(50, 800)
    self.t = random.randint(0, 20)

  def update(self):
    self.walk()
    self.rect.center = (self.x + sin(self.t) * 10, self.y + cos(self.t)**2 * 10)
