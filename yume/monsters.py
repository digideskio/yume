import pygame
import random
from math import *
from yume import *
from yume.resource import *
from pygame import Rect
from yume import gfx

class Monster(gfx.Drawable):
  hp = 10
  poison_duration_left = 0
  poison_strength = 0
  speed = 1
  graphic = gfx.MonsterGFX
  transparent = True

  traits = 'ahsvrpPi'

  def draw(self, screen):
    screen.blit(self.gfx.surface, (self.x - self.gfx.width / 2, self.y - self.gfx.height / 2))
    self.gfx.next_frame()

  def poison(self, strength, duration, dealer):
    self.poison_strength = strength
    self.poison_duration_left = duration
    self.killer = dealer

  def draw_hp_bar(self, screen):
    color = (0, 255, 0) if self.poison_duration_left else (255, 0, 0)
    wid = self.gfx.width * self.hp / self.max_hp
    pygame.draw.line(screen, color, (self.x - self.gfx.width / 2, self.y - self.gfx.height), (self.x - self.gfx.width / 2 + wid, self.y - self.gfx.height), 2)
    if self.shield > 0:
      wid = self.gfx.width * self.shield / self.max_shield
      offset = 1 if self.hp < self.max_hp else 0
      pygame.draw.line(screen, (0, 0, 255), (self.x - self.gfx.width / 2, self.y - self.gfx.height+offset), (self.x - self.gfx.width / 2 + wid, self.y - self.gfx.height+offset), 2)

  # "meta" needs to be of type yume.levels.MetaMonster
  def __init__(self, meta, arena):
    gene = meta.gene
    if 'B' in gene:
      self.graphic = gfx.Monster2GFX

    gfx.Drawable.__init__(self)
    self.meta = meta
    self.stagger = 0
    self.waypoint_index = 1
    self.waypoints = [(0, 0)]
    self.calc_vector = True
    self.killer = None
    self.tunnel_entered = False

    # undefined
    self.vector_y = 0
    self.vector_x = 0
    self.vector_length = 0
    self.current_node_index = None

    boss = 'B' in gene
    r = arena.rect
    self.hp = (gene.count('h') + 2) * 8
    if boss:
      self.hp *= 4
    self.max_hp = self.hp
    self.speed = 0.7 + (gene.count('v') * 0.15)
    self.shield = gene.count('s') * 3
    self.max_shield = self.shield
    self.worth = log(len(gene) + 2)
    self.armor = gene.count('a') / 6.0
    self.poison_resistance = 1.0 / (1 + gene.count('i') / 2.0)
    if boss:
      self.armor += 2
      self.worth *= 5
    self.recovery = gene.count('r') * 0.05
    self.shield_recovery = gene.count('r') * 0.2

    # =====================
    # find starting position
    ep = arena.level.entry_points
    x, y = ep[(gene.count('p') + 2 * gene.count('P')) % len(ep)]
    self.x, self.y = arena.cell_to_pos(x + 2, y + 2)

  def update(self):
    if self.current_node_index is None:
      self.find_next_waypoint()
    if self.hp <= 0:
      return

    self.shield = min(self.max_shield, self.shield + self.shield_recovery)

    if self.poison_duration_left:
      self.damage(self.poison_strength, self.killer)
      self.poison_duration_left -= 1
    else:
      self.poison_strength = 0
      self.hp = min(self.max_hp, self.hp + self.recovery)

    self.position += self.speed
    if self.position >= self.vector_length:
      self.find_next_waypoint()

    self.x = self.base_x + self.vector_x * self.position
    self.y = self.base_y + self.vector_y * self.position
    self.rect.center = (self.x, self.y)
    if self.tunnel_entered:
      self.meta.fitness += self.speed
    else:
      self.meta.fitness += self.speed * 0.1

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
        self.meta.fitness += 2000
        self.die()
      else:
        self.meta.fitness += 500
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
