import os
import pygame
import time
from pygame.locals import *
from pygame import Rect
from yume.resource import *
from yume.gfx import get_gfx
from yume.levels import *
from yume.towers import *
from yume import *
from yume import gfx

class Interface(object):
  def __init__(self):
    self.mana_max = 300.0
    self.mana = 100.0
    self.mana_regen = 0.1
    self.dragging = None
    self.dragged_surface = None
    self.arena = Arena()
    Global.arena = self.arena
    self.bottom1 = Bottom()
    self.bottom2 = Bottom()
    self.bottom3 = Bottom()
    self.costbar = get_sprite('cost.png', dirty=True)
    self.menubar = get_sprite('menu.png', dirty=True)
    self.wave_marker = pygame.Surface((30, ARENA_HEIGHT))
    self.renderer = pygame.sprite.RenderPlain([self.bottom1, self.bottom2,
      self.bottom3, self.menubar])
    self.renderer2 = pygame.sprite.RenderPlain([])
    self.last_update = time.time()
    self.font = get_font()

    self.manabar = get_gfx(gfx.ManaBar, (1, ))
    self.manabar_x = -self.manabar.width

  def update(self):
    dt = time.time() - self.last_update
    self.last_update = time.time()
    self.mana = max(0, min(self.mana + self.mana_regen * dt, self.mana_max))

  def crash(self):
    self.mana = int(self.mana * 0.5)

  def distance_between(self, x1, y1, x2, y2):
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)

  def get_monsters_in_range(self, x1, y1, rnge):
    for monster in self.arena.creeps:
      x2, y2 = monster.rect.center
      if sqrt((x1-x2) ** 2 + (y1-y2) ** 2) < rnge:
        yield monster

  def get_random_monster_in_range(self, x1, y1, rnge, n=1):
    monsters = list(self.get_monsters_in_range(x1, y1, rnge))
    if len(monsters) >= n:
      return random.sample(monsters, n)
    return monsters

  def draw(self, screen):
    w, h = screen.get_size()
    self.bottom1.rect.bottomleft = 0, h
    self.bottom2.rect.bottomleft = 500, h
    self.bottom3.rect.bottomleft = 1000, h

    manapos = self.manabar.width / self.mana_max * self.mana - self.manabar.width
    current_manapos = self.manabar_x
    diff = current_manapos - manapos
    if abs(diff) > 2:
      manapos += diff * 0.80
    self.manabar_x = manapos
    screen.blit(self.manabar.surface, (manapos, 2))
    self.manabar.next_frame()

    if self.dragging:
      pos = self.costbar.rect.width / self.mana_max * self.dragging.cost - self.costbar.rect.width
      self.costbar.rect.topleft = pos, 2

    self.menubar.rect.topright = w, 0
    self.arena.update()
    self.arena.draw(screen)
    self.renderer.update()
    self.renderer2.update()
    self.renderer.draw(screen)
    self.renderer2.draw(screen)
    if self.dragging and self.dragged_surface:
      screen.blit(self.dragged_surface, pygame.mouse.get_pos())
    x, y = 0, SCREEN_HEIGHT
    color = 255
    for text in Global.yume.log_entries:
      y -= self.font.get_height() + 2
      text = self.font.render(text, 1, (color, color, color))
      color -= 24
      screen.blit(text, (x, y))
    y = ARENA_TOP_POS + self.arena.delay * 10
    for wave in self.arena.level.waves:
      if y > ARENA_HEIGHT:
        break
      rect = Rect((0, y), (20, 20))
      pygame.draw.rect(screen, (100, 0, 100), rect)
      y += max(25, wave.delay * 10)

  def click(self, pos, button):
    if button == 1:
      if self.arena.rect.collidepoint(pos):
        if self.dragging:
          if self.mana >= self.dragging.cost:
            released = self.arena.release(self.dragging, pos)
            if released:
              self.mana -= self.dragging.cost
              self.undrag()
          else:
            Global.yume.log("Not enough mana!")
    if self.dragging:
      self.undrag()

  def undrag(self):
    self.dragging = None
    self.renderer2.remove(self.costbar)

  def press(self, key):
    if key == K_1:
      self.drag(TowerBubble)
    if key == K_SPACE:
      self.arena.delay = min(1, self.arena.delay)

  def drag(self, obj):
    self.dragging = obj
    self.dragged_surface = get_gfx(obj.graphic, (0, 0)).surface
    self.renderer2.add(self.costbar)

class Arena(object):
  def __init__(self):
    def makelayer():
      layer = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
      layer.set_colorkey((0, 0, 0))
      return layer.convert()

    self.creeplayer = makelayer()
    self.projectilelayer = makelayer()

    self.rect = Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self.renderer = pygame.sprite.RenderPlain([])

    self.load_level(LevelInvocation)

  def load_level(self, cls):
    self.level = cls()
    self.level.initialize()
    Global.level = self.level
    self.last_update = 0
    self.active_waves = set()
    self.delay = 1
    self.cells = [[1] * CELLS_X for _ in range(CELLS_Y)]

    self.creeps = list()
    self.projectiles = list()
    self.towers = list()

  def release(self, obj, pos):
    if issubclass(obj, Tower):
      pos = (pos[0] - ARENA_LEFT_POS, pos[1] - ARENA_TOP_POS)
      self.createTower(obj, pos)
      return True

  def createTower(self, cls, pos):
    tower = cls()
    tower.move(*pos)
    self.towers.append(tower)

  def update(self):
    self.renderer.update()
    if self.last_update:
      dt = time.time() - self.last_update

      for mob in list(self.creeps):
        if mob.hp <= 0:
          self.creeps.remove(mob)
          if mob.killer:
            Global.yume.interface.mana += mob.worth
        mob.update()

      for tower in list(self.towers):
        tower.update()

      for projectile in list(self.projectiles):
        projectile.update()

      for wave in list(self.active_waves):
        if wave.monster_queue:
          wave.monster_tick -= dt
          if wave.monster_tick < 0:
            monster = wave.monster_queue.pop()
            self.spawn(monster)
            wave.monster_tick = wave.monster_delay 

      self.delay -= dt
      if self.level.waves and self.delay < 0:
        wave = self.level.waves.popleft()
        wave.engage()
        self.active_waves.add(wave)
        self.delay = wave.delay

    self.last_update = time.time()

  def draw(self, screen):
    self.level.draw(screen)
    self.creeplayer.fill((0, 0, 0))
    self.projectilelayer.fill((0, 0, 0))
    for creep in self.creeps:
      creep.draw(self.creeplayer)
    for tower in list(self.towers):
      tower.draw(self.projectilelayer)
    for projectile in self.projectiles:
      projectile.draw(self.projectilelayer)
    screen.blit(self.creeplayer, (ARENA_LEFT_POS, ARENA_TOP_POS))
    screen.blit(self.projectilelayer, (ARENA_LEFT_POS, ARENA_TOP_POS))
    self.renderer.draw(screen)
    self.level.draw_above(screen)

  def spawn(self, monster):
    mon = monster()
    mon.x, mon.y = self.level.waypoints_scaled[0]
    mon.waypoints = self.level.waypoints_scaled
    self.creeps.append(mon)

class Bottom(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = load_image('foot.png')
    self.rect = self.image.get_rect()
