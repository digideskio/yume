import pygame
import random
from math import *
from yume import *
from yume.resource import *
from pygame import Rect
from yume import gfx

class Monster(gfx.Drawable):
  worth = 4
  hp = 10
  speed = 1
  graphic = gfx.MonsterGFX

  def __init__(self, gene, arena):
    gfx.Drawable.__init__(self)
    self.stagger = 0
    self.waypoint_index = 1
    self.waypoints = [(0, 0)]
    self.calc_vector = True
    self.vector_y = 0
    self.vector_x = 0
    self.killer = None

    # =====================
    r = arena.rect
    self.hp = (gene.count('a') + 1) * 10
    self.speed = 1
    worth = log(len(gene) + 2)

    ep = arena.level.entry_points
    x, y = ep[gene.count('b') % len(ep)]
    self.x, self.y = arena.cell_to_pos(x + 2, y + 2)
#    if (gene.count('b') / 2) % 2:
#      if (gene.count('c') / 2) % 2:
#        self.x, self.y = r.midleft
#      else:
#        self.x, self.y = r.midtop
#    else:
#      if (gene.count('c') / 2) % 2:
#        self.x, self.y = r.midright
#      else:
#        self.x, self.y = r.midbottom

  def update(self):
    if self.hp <= 0:
      return
    brain_pos = Global.arena.brain_pos
    if self.stagger > 0:
      self.stagger -= 1
      return
    x = brain_pos[0] - self.x
    y = brain_pos[1] - self.y
    if self.calc_vector:
      rotation = atan2(y, x)
      self.vector_x = cos(rotation)
      self.vector_y = sin(rotation)
      self.calc_vector = False
    distance = sqrt(x*x+y*y)
    if distance < 10:
      Global.yume.interface.crash()
      self.die()
    else:
      self.x += self.vector_x * self.speed
      self.y += self.vector_y * self.speed

    self.rect.center = (self.x, self.y)

  def die(self):
    self.hp = 0

  def damage(self, damage, dealer):
    if self.hp > 0:
      self.hp -= damage
      self.stagger = max(10, self.stagger)
      if self.hp <= 0:
        self.killer = dealer
