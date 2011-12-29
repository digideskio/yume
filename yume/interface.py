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
    self.mana = 300.0
    self.mana_regen = 0.1
    self.adren = 0.0
    self.adren_max = 100.0
    self.adren_baseline = 0.0
    self.adren_regen = 1
    self.adren_baseline_regen = -0.1
    self.dragging = None
    self.dragged_surface = None
    self.arena = Arena()
    Global.arena = self.arena
    self.wave_marker = pygame.Surface((30, ARENA_HEIGHT))
    self.renderer2 = pygame.sprite.RenderPlain([])
    self.last_update = time.time()
    self.font = get_font()

    self.adrenbar = get_gfx(gfx.AdrenalineBar, (1, ))
    self.adrenbar_x = -self.adrenbar.width
    self.manabar = get_gfx(gfx.ManaBar, (1, ))
    self.manabar_x = -self.manabar.width
    self.costbar = get_gfx(gfx.CostBar, (1, ))
    self.costbar_x = -self.costbar.width

  def update(self):
    dt = time.time() - self.last_update
    self.last_update = time.time()
    self.mana = max(0, min(self.mana + self.mana_regen * dt, self.mana_max))

    # adrenaline foo
    self.adren_baseline = max(0, min(self.adren_baseline +
      self.adren_baseline_regen * dt, self.adren_max))
    if self.adren >= self.adren_max:
      Global.yume.log("YOU DIE!!11")
      self.adren = self.adren_max
    else:
      diff = self.adren - self.adren_baseline
      if abs(diff) < self.adren_regen * 2:
        self.adren = self.adren_baseline
      elif diff > 0:
        self.adren = max(0, self.adren - self.adren_regen * dt)
      else:
        self.adren = max(0, self.adren + self.adren_regen * dt)

  def crash(self):
    self.adren_baseline += 10
    self.adren += 10
    self.mana = int(self.mana * 0.8)

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

    self.arena.update()
    self.arena.draw(screen)

    manapos = self.manabar.width / self.mana_max * self.mana - self.manabar.width
    current_manapos = self.manabar_x
    diff = current_manapos - manapos
    if abs(diff) > 2:
      manapos += diff * 0.80
    self.manabar_x = manapos
    screen.blit(self.manabar.surface, (manapos, 2))
    self.manabar.next_frame()

    adrenpos = self.adrenbar.width / self.adren_max * self.adren - self.adrenbar.width
    current_adrenpos = self.adrenbar_x
    diff = current_adrenpos - adrenpos
    if abs(diff) > 2:
      adrenpos += diff * 0.80
    self.adrenbar_x = adrenpos
    screen.blit(self.adrenbar.surface, (adrenpos, 22))
    self.adrenbar.next_frame()

    if self.dragging:
      pos = self.costbar.width / self.mana_max * self.dragging.cost - self.costbar.width
      self.costbar_x = pos, 2
      screen.blit(self.costbar.surface, (pos, 2))
      self.costbar.next_frame()

    self.renderer2.update()
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
#    y = ARENA_TOP_POS + self.arena.delay * 10
#    for wave in self.arena.level.waves:
#      if y > ARENA_HEIGHT:
#        break
#      rect = Rect((0, y), (20, 20))
#      pygame.draw.rect(screen, (100, 0, 100), rect)
#      y += max(25, wave.delay * 10)

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

  def press(self, key):
    if key == K_1:
      self.drag(TowerBubble)
    if key == K_0:
      if not self.arena.brain_pos:
        self.drag(TowerBrain)
    if key == K_SPACE:
      self.arena.delay = min(1, self.arena.delay)

  def drag(self, obj):
    self.dragging = obj
    self.dragged_surface = get_gfx(obj.graphic, (0, 0)).surface

class Arena(object):
  def __init__(self):
    self.rect = Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self.renderer = pygame.sprite.RenderPlain([])

    self.background = get_gfx(gfx.Background, (1, 1))
    self.bg_tick = 0

    self.load_level(Level1)

  def pos_to_cell(self, x, y):
    x = int((x + ARENA_LEFT_POS) / 25)
    y = int((y + ARENA_TOP_POS) / 25)
    return x, y

  def cell_to_pos(self, x, y):
    x = int(x * 25 - ARENA_LEFT_POS + 1)
    y = int(y * 25 - ARENA_TOP_POS + 1)
    return x, y

  def load_level(self, cls):
    self.level = cls()
    Global.level = self.level
    self.last_update = 0
    self.delay = 1
    self.monster_timer = 0
    self.tower_positions = self.level.cells

    self.creeps = list()
    self.projectiles = list()
    self.towers = list()
    self.brain_pos = None
    self.monsters_left = set()
    self.grid = self.level.make_grid((100, 0, 0))
    #print(self.level.entry_points)
    #print(self.level.cells)
    #raise SystemExit()
    Global.yume.log("Press 0 and place your brain to start the game")

  def release(self, obj, pos):
    if issubclass(obj, Tower):
      x, y = self.pos_to_cell(pos[0], pos[1])
      pos = x, y
      pos_ = x - 2, y - 2
      if pos_ in self.tower_positions:
        Global.yume.log("Invalid position")
        return False
      else:
        self.tower_positions[pos] = self.createTower(obj, self.cell_to_pos(x, y))
      return True

  def createTower(self, cls, pos):
    tower = cls()
    tower.move(*pos)
    self.towers.append(tower)
    if cls == TowerBrain:
      self.brain_pos = pos
    return tower

  def update(self):
    self.renderer.update()
    if self.last_update and self.brain_pos:
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

      if self.monster_timer > 0:
        self.monster_timer -= dt
      elif self.monsters_left:
        monster = Monster(self.monsters_left.pop(), self)
        self.spawn(monster)
        self.monster_timer = 0.5
      else:
        Global.yume.log("Gene: %s" % self.level.gene)
        self.monster_timer = 3
        self.monsters_left = self.level.get_monsters()
        self.level.mutate()

    self.last_update = time.time()

  def draw(self, screen):
    screen.blit(self.background.surface, (0, 0))
    screen.blit(self.background.surface, (0, 0))
    #screen.fill((0, 0, 0))
    self.bg_tick += 1
    if self.bg_tick >= 3:
      self.background.next_frame()
      self.bg_tick = 0
    if Global.face.dragging:
      screen.blit(self.grid, (ARENA_TOP_POS, ARENA_LEFT_POS))
    for tower in list(self.towers):
      tower.draw(screen)
    for creep in self.creeps:
      creep.draw(screen)
    for projectile in self.projectiles:
      projectile.draw(screen)

  def spawn(self, mon):
    self.creeps.append(mon)
