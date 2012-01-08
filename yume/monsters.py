import pygame
import random
from math import *
from yume import *
from yume.resource import *
from pygame import Rect
from yume import gfx

class Monster(gfx.Drawable):
  hp = 10
  speed = 1
  graphic = gfx.MonsterGFX
  transparent = True

  traits = 'ahpPsvr'

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x - self.gfx.width / 2, self.y - self.gfx.height / 2))
    self.gfx.next_frame()

  def draw_hp_bar(self, screen):
    wid = self.gfx.width * self.hp / self.max_hp
    pygame.draw.line(screen, (255, 0, 0), (self.x - self.gfx.width / 2, self.y - self.gfx.height), (self.x - self.gfx.width / 2 + wid, self.y - self.gfx.height), 2)
    if self.shield > 0:
      wid = self.gfx.width * self.shield / self.max_shield
      offset = 1 if self.hp < self.max_hp else 0
      pygame.draw.line(screen, (0, 0, 255), (self.x - self.gfx.width / 2, self.y - self.gfx.height+offset), (self.x - self.gfx.width / 2 + wid, self.y - self.gfx.height+offset), 2)

  def __init__(self, gene, arena):
    gfx.Drawable.__init__(self)
    self.stagger = 0
    self.waypoint_index = 1
    self.waypoints = [(0, 0)]
    self.calc_vector = True
    self.killer = None
    self.fitness = 0
    self.tunnel_entered = False

    # undefined
    self.vector_y = 0
    self.vector_x = 0
    self.vector_length = 0
    self.current_node_index = None

    # =====================
    # find starting position
    r = arena.rect
    self.hp = (gene.count('h') + 2) * 8
    self.max_hp = self.hp
    self.speed = 1 + (gene.count('v') * 0.1)
    self.shield = gene.count('s') * 3
    self.max_shield = self.shield
    self.worth = log(len(gene) + 2)
    self.armor = gene.count('a') / 6.0
    self.recovery = gene.count('r') * 0.05
    self.shield_recovery = gene.count('r') * 0.2
    self.gene = gene

    ep = arena.level.entry_points
    x, y = ep[(gene.count('p') + 2 * gene.count('P')) % len(ep)]
    self.x, self.y = arena.cell_to_pos(x + 2, y + 2)

  def update(self):
    if self.current_node_index is None:
      self.find_next_waypoint()
    if self.hp <= 0:
      return

    self.shield = min(self.max_shield, self.shield + self.shield_recovery)
    self.hp = min(self.max_hp, self.hp + self.recovery)

    self.position += self.speed
    if self.position >= self.vector_length:
      self.find_next_waypoint()

    self.x = self.base_x + self.vector_x * self.position
    self.y = self.base_y + self.vector_y * self.position
    self.rect.center = (self.x, self.y)
    if self.tunnel_entered:
      self.fitness += self.speed
    else:
      self.fitness += self.speed * 0.1

  def look_again_for_tunnel_entry(self):
    if not self.tunnel_entered:
      self.current_node_index = None
      self.find_next_waypoint()

  def find_next_waypoint(self):
    self.base_x = self.x
    self.base_y = self.y
    self.vector_length = 0

    nodes = Global.arena.nodes
    if self.current_node_index == None:
      self.current_node_index = len(nodes) - 1
    else:
      self.tunnel_entered = True
      if self.current_node_index <= 0:
        Global.yume.interface.crash()
        self.fitness += 2000
        self.die()
      else:
        self.fitness += 500
        self.current_node_index -= 1

    node = nodes[self.current_node_index]
    x = node.x + 12 - self.x
    y = node.y + 12 - self.y
    rotation = atan2(y, x)
    self.vector_x = cos(rotation)
    self.vector_y = sin(rotation)
    self.vector_length = sqrt(x**2 + y**2)
    self.position = 0

  def die(self):
    self.hp = 0
#    self.fitness = (len(Global.arena.nodes) - 1 - self.current_node_index) * 10
#    print("died at fitness %d" % self.fitness)

  def damage(self, damage, dealer, ignore_shield=False):
    if self.hp > 0:
      damage = max(0.1, damage - self.armor)
      if ignore_shield or self.shield == 0:
        self.hp -= damage
      elif self.shield > damage:
        self.shield -= damage
      else:
        self.hp -= damage - self.shield
        self.shield = 0
      self.stagger = max(10, self.stagger)
      if self.hp <= 0:
        self.die()
        self.killer = dealer
