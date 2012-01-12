import os
import pygame
import time
import itertools
from math import *
from pygame.locals import *
from pygame import Rect
from yume.resource import *
from yume.gfx import get_gfx
from yume.levels import *
from yume.towers import *
from yume.widgets import MenuButton
from yume.items import AdrenalinePill, ManaPotion, SedativePill
from yume import *
from yume import gfx
from yume.lib import cached_method, OpenStruct

def manabar_pos_transform(mana):
#  return x/400 if x <= 200 else (log(x/2000.0+1)+0.405 if x <= 1000 else x/20000 + 0.76)
  if mana <= 200:
    return mana / 400.0
  if mana <= 1000:
    return log(mana/2000.0+1)+0.405 
  if mana < 4800:
    return mana / 20000 + 0.76
  return 1

class Interface(object):
  def __init__(self):
    self.arena = Arena()
    Global.arena = self.arena
    self.adrenbar = get_gfx(gfx.AdrenalineBar, (1, ))
    self.adrenbar_x = -self.adrenbar.width
    self.adren_costbar = get_gfx(gfx.AdrenalineCostBar, (1, ))
    self.manabar = get_gfx(gfx.ManaBar, (1, ))
    self.manabar_x = -self.manabar.width
    self.costbar = get_gfx(gfx.CostBar, (1, ))
    self.costbar_x = -self.costbar.width

    self.initialize_buttons()
    self.load_level(Level1)

  def load_level(self, level):
    self.score = 0
    self.mana = 100.0
    self.mana_regen = 0.1
    self.adren = 0.0
    self.adren_max = 100.0
    self.adren_baseline = 0.0
    self.adren_regen = 1
    self.adren_baseline_regen = -0.1

    self.basic_mana_regen = self.mana_regen
    self.basic_adren_regen = self.adren_regen
    self.basic_adren_baseline_regen = self.adren_baseline_regen

    self.items = 1
    self.items_active = []
    self.dragging = None
    self.dragged_surface = None
    self.tooltip = None

    self.last_update = time.time()
    self.font = get_font()
    self.game_over = False

    self.arena.load_level(level)
    self.menu = [self.button_definitions.brain]
    Global.yume.log("Place the Dream Stone to start the game.")

  def initialize_buttons(self):
    buttons = OpenStruct()

    buttons['bubble'] = button = MenuButton(gfx.TowerBubbleGFX)
    button.action = lambda: Global.face.press(K_1)
    button.activation_test = lambda: Global.face.mana >= TowerBubble.cost \
        and Global.face.adren + TowerBubble.adrenaline_cost <= Global.face.adren_max
    button.tooltip = "Create a Bubble Tower"

    buttons['lazor'] = button = MenuButton(gfx.TowerLazorGFX)
    button.action = lambda: Global.face.press(K_2)
    button.activation_test = lambda: Global.face.mana >= TowerLazor.cost \
        and Global.face.adren + TowerLazor.adrenaline_cost <= Global.face.adren_max
    button.tooltip = "Create a Lazor Tower"

    buttons['virus'] = button = MenuButton(gfx.TowerVirusGFX)
    button.action = lambda: Global.face.press(K_3)
    button.activation_test = lambda: Global.face.mana >= TowerVirus.cost \
        and Global.face.adren + TowerVirus.adrenaline_cost <= Global.face.adren_max
    button.tooltip = "Create a Virus Tower"

    buttons['guardian'] = button = MenuButton(gfx.TowerGuardianGFX)
    button.action = lambda: Global.face.press(K_4)
    button.activation_test = lambda: Global.face.mana >= TowerGuardian.cost \
        and Global.face.adren + TowerGuardian.adrenaline_cost <= Global.face.adren_max
    button.tooltip = "Create a Guardian Tower"

    buttons['brain'] = button = MenuButton(gfx.TowerBrain)
    button.action = lambda: Global.face.press(K_0)
    button.tooltip = "Create a Brain"

    buttons['node'] = button = MenuButton(gfx.TowerNode)
    button.action = lambda: Global.face.press(K_9)
    button.activation_test = lambda: Global.face.mana >= TowerNode.cost \
        and Global.face.adren + TowerNode.adrenaline_cost <= Global.face.adren_max
    button.tooltip = "Create a Node"

    buttons['manaPotion'] = button = MenuButton(ManaPotion.graphic)
    button.action = lambda: Global.face.consume(ManaPotion)
    button.activation_test = lambda: Global.face.items > 0
    button.tooltip = "Consume a Mana Potion"

    buttons['adrenPill'] = button = MenuButton(AdrenalinePill.graphic)
    button.action = lambda: Global.face.consume(AdrenalinePill)
    button.activation_test = lambda: Global.face.items > 0
    button.tooltip = "Consume an Adrenaline Pill"

    buttons['sedative'] = button = MenuButton(SedativePill.graphic)
    button.action = lambda: Global.face.consume(SedativePill)
    button.activation_test = lambda: Global.face.items > 0
    button.tooltip = "Consume a Sedative Pill"
    self.button_definitions = buttons

  def consume(self, item):
    if self.items > 0:
      self.items -= 1
      item_instance = item(self)
      self.items_active.append(item_instance)
      Global.yume.log("Yummy %s" % item_instance.name)

  def update(self):
    dt = time.time() - self.last_update
    self.last_update = time.time()
    if self.game_over:
      return

    for item in tuple(self.items_active):
      item.update(dt)
      if item.time_left < 0:
        item.destroy()
        self.items_active.remove(item)

    self.mana = max(0, self.mana + self.mana_regen * dt)

    # adrenaline foo
    self.adren_baseline = max(0, min(self.adren_baseline +
      self.adren_baseline_regen * dt, self.adren_max))
    if self.adren >= self.adren_max:
      self.adren = self.adren_max
    else:
      diff = self.adren - self.adren_baseline
      if abs(diff) < self.adren_regen * 2:
        self.adren = self.adren_baseline
      elif diff > 0:
        self.adren = max(0, self.adren - self.adren_regen * dt)
      else:
        self.adren = max(0, self.adren + self.adren_regen * dt)

    if pygame.mouse.get_pos() == (0, 0):
      self.tooltip = "This is the edge. XD"
    else:
      self.tooltip = None

  def crash(self):
    self.adren_baseline += 10
    self.adren += 10
    self.check_for_death()

  def check_for_death(self):
    if self.adren >= self.adren_max or self.adren_baseline >= self.adren_max:
      Global.yume.log("You woke up!! Game Over!")
      self.game_over = True

  def distance_between(self, x1, y1, x2, y2):
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)

  def get_monsters_in_range(self, x1, y1, rnge):
    for monster in self.arena.creeps:
      x2, y2 = monster.rect.center
      if sqrt((x1-x2) ** 2 + (y1-y2) ** 2) < rnge:
        yield monster

  def get_monsters_in_rect(self, rect):
    for monster in self.arena.creeps:
      if rect.collidepoint(monster.rect.center):
        yield monster

  def get_monsters_in_line(self, x1, y1, x2, y2, width):
    for monster in self.arena.creeps:
      try:
        dx, dy = x2 - x1, y2 - y1
        slope = float(dy) / dx
        d_vert = monster.y - (slope * monster.x + (y1 - slope * x1))
        slope = float(dx) / dy
        d_hori = monster.x - (slope * monster.y + (x1 - slope * y1))
        dist = sqrt((d_hori*d_hori * d_vert*d_vert) / (d_hori*d_hori + d_vert*d_vert))
        if dist >= width:
          continue
      except ZeroDivisionError:
        pass
      if monster.x + width >= min(x1, x2) and monster.x - width <= max(x1, x2) and \
         monster.y + width >= min(y1, y2) and monster.y - width <= max(y1, y2):
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

    offset = 10
    logbase = 1.1

#    manapos = self.manabar.width / self.mana_max * self.mana - self.manabar.width + 40
    manapos = manabar_pos_transform(self.mana) * self.manabar.width - self.manabar.width + 40
#    manapos = self.manabar.width / self.mana_max * self.mana - self.manabar.width + 40
    current_manapos = self.manabar_x
    diff = current_manapos - manapos
    if abs(diff) > 2:
      manapos += diff * 0.80
    self.manabar_x = manapos
    screen.blit(self.manabar.surface, (manapos, 2))
    self.manabar.next_frame()

    if self.dragging:
      pos = manabar_pos_transform(self.dragging.cost) * self.costbar.width - self.costbar.width + 40
      self.costbar_x = pos, 2
      screen.blit(self.costbar.surface, (pos, 5))
      self.costbar.next_frame()

      pos = self.adrenbar.width / self.adren_max * min(self.adren_max, self.adren + self.dragging.adrenaline_cost) - self.adrenbar.width + 40
      screen.blit(self.adren_costbar.surface, (pos, 22))

#    adren = self.adren + self.dragging.adrenaline_cost if self.dragging else self.adren
#    adren = min(self.adren_max, adren)
    adrenpos = self.adrenbar.width / self.adren_max * min(self.adren_max, self.adren) - self.adrenbar.width + 40
    current_adrenpos = self.adrenbar_x
    diff = current_adrenpos - adrenpos
    if abs(diff) > 2:
      adrenpos += diff * 0.80
    self.adrenbar_x = adrenpos
    screen.blit(self.adrenbar.surface, (adrenpos, 22))
    self.adrenbar.next_frame()


    if self.dragging and self.dragged_surface:
      screen.blit(self.dragged_surface, pygame.mouse.get_pos())

    self.draw_console(screen)
    self.draw_status(screen)

    x, y = 0, 0
    for button in self.menu:
      if button:
        button.draw(screen, (x, y))
        y += button.height
      else:
        y += MenuButton.height

  def draw_console(self, screen):
    if self.tooltip:
      text = self.font.render(self.tooltip, 1, (150, 255, 150))
      y = SCREEN_HEIGHT - text.get_rect().height
      screen.fill((0, 0, 0), text.get_rect().inflate(10, 10).move(0, y))
      screen.blit(text, (0, y))
    else:
      color = 255
      x, y = 0, SCREEN_HEIGHT
      for text in Global.yume.log_entries:
        if text is not None:
          y -= self.font.get_height() + 2
          text = self.font.render(text, 1, (color, color, color))
          screen.blit(text, (x, y))
        color -= 24

  def draw_status(self, screen):
    y = 50
    def round_(f):
      return int(f * 10) / 10.0

    data = dict(fps = round_(Global.yume.clock.get_fps()),
        mana = int(self.mana),
        adrenaline = int(self.adren),
        adrenalinemax = int(self.adren_max),
        genepool = self.arena.genepool_info,
        level = self.arena.level.level_number,
        items = self.items,
        score = self.score)
    status_template = STATUS_TEMPLATE.format(**data)
    for line in status_template.split("\n"):
      text = self.font.render(line, 1, (200, 200, 200))
      x = SCREEN_WIDTH - text.get_rect().width
      screen.blit(text, (x, y))
      y += text.get_rect().height + 2

  def click(self, pos, button):
    if button == 1:
      if pos[0] <= MenuButton.width:
        try:
          button = self.menu[int(pos[1] / MenuButton.height)]
        except:
          pass
        else:
          if button:
            button.action()
          return
      if self.arena.rect.collidepoint(pos):
        if self.dragging:
          if self.mana >= self.dragging.cost:
            if self.adren_max - self.adren > self.dragging.adrenaline_cost:
              released = self.arena.release(self.dragging, pos)
              if released:
                self.mana -= self.dragging.cost
                self.adren += self.dragging.adrenaline_cost
                self.undrag()
            else:
              Global.yume.log("Too much adrenaline!")
          else:
            Global.yume.log("Not enough mana!")
    if self.dragging:
      self.undrag()

  def undrag(self):
    self.dragging = None

  def press(self, key):
    if key == K_1:
      self.drag(TowerBubble)
    if key == K_2:
      self.drag(TowerLazor)
    if key == K_3:
      self.drag(TowerVirus)
    if key == K_4:
      self.drag(TowerGuardian)
    if key == K_0:
      if not self.arena.brain:
        self.drag(TowerBrain)
    if key == K_9:
      self.drag(TowerNode)
    if key == K_r:
      self.load_level(Level1)
    if key == K_SPACE:
      self.arena.delay = min(1, self.arena.delay)

  def drag(self, obj):
    self.dragging = obj
    self.dragged_surface = get_gfx(obj.graphic, (1, 1), transparency=True).surface

class Arena(object):
  def __init__(self):
    self.rect = Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self._cache = {}

    if Global.yume.test_mode:
      self.background = get_gfx(gfx.TestBackground, (1, 1))
    else:
      [gfx.get_surface(gfx.Background, i, 'Background') for i in range(gfx.Background.frames)]
      self.background = get_gfx(gfx.Background, (1, 1))
    self.bg_tick = 0

  def pos_to_cell(self, x, y):
    x = int((x - ARENA_LEFT_POS) / 25)
    y = int((y - ARENA_TOP_POS) / 25)
    return x, y

  def cell_to_pos(self, x, y):
    x = int(x * 25 + ARENA_LEFT_POS + 1)
    y = int(y * 25 + ARENA_TOP_POS + 1)
    return x, y

  def load_level(self, cls):
    self.level = cls()
    Global.level = self.level
    self.last_update = 0
    self.delay = 1
    self.monster_timer = 0
    self.tower_positions = self.level.cells

    self.dead_creeps = list()
    self.creeps = list()
    self.projectiles = list()
    self.towers = list()
    self.brain = None
    self.nodes = []
    self.pools = []
    self.grid = self.level.make_grid((100, 0, 0))
    self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    self.surface.set_colorkey((0, 0, 0))
    self.surface.convert_alpha()
    self.genepool_info = ""

  def release(self, obj, pos):
    if issubclass(obj, Tower):
      x, y = self.pos_to_cell(pos[0], pos[1])
      pos = x, y
      if pos not in self.tower_positions:
        Global.yume.log("Invalid position")
        return False
      elif obj == TowerNode and not self.node_allowed_here(x, y):
        Global.yume.log("Out of range")
        return False
      elif self.tower_positions[pos]:
        Global.yume.log("There is already a tower on this position!")
        return False
      else:
        self.tower_positions[pos] = self.createTower(obj, (x, y))
      return True

  def createTower(self, cls, pos):
    tower = cls()
    (a, b) = self.cell_to_pos(pos[0], pos[1])
    tower.move((a, b), pos)
    self.towers.append(tower)
    if cls == TowerBrain:
      self.brain = tower
      self.nodes = [tower]
      Global.face.menu.remove(Global.face.button_definitions['brain'])
      Global.face.menu.append(Global.face.button_definitions['bubble'])
      Global.face.menu.append(Global.face.button_definitions['lazor'])
      Global.face.menu.append(Global.face.button_definitions['virus'])
      Global.face.menu.append(Global.face.button_definitions['guardian'])
      Global.face.menu.append(None)
      Global.face.menu.append(Global.face.button_definitions['node'])
      Global.face.menu.append(None)
      Global.face.menu.append(Global.face.button_definitions['manaPotion'])
      Global.face.menu.append(Global.face.button_definitions['adrenPill'])
      Global.face.menu.append(Global.face.button_definitions['sedative'])
    elif cls == TowerNode:
      self.build_node(tower)
      self.nodes.append(tower)
    elif cls == TowerBubble:
      bubbles = sum(isinstance(tower, TowerBubble) for tower in self.towers)
      TowerBubble.special_chance = 0.03 / bubbles
    return tower

  def build_node(self, tower):
    last_node = self.nodes[-1]
    self.nodes.append(tower)
    nodex, nodey = last_node.gridpos
    mousex, mousey = tower.gridpos
    for x in range(40):
      for y in range(28):
        if self.node_path(nodex, nodey, x, y, mousex, mousey):
          self.tower_positions[(x, y)] = 1
    line_color = [(255, 255, 255), (200, 200, 200)]
    line_origin = (last_node.x + 12, last_node.y + 12)
    line_target = (tower.x + 12, tower.y + 12)
    pygame.draw.line(self.surface, line_color[0], line_origin, line_target, 3)
    pygame.draw.line(self.surface, line_color[1], line_origin, line_target, 1)
    self.surface = self.surface.convert_alpha()
    for monster in self.creeps:
      monster.look_again_for_tunnel_entry()

  def update(self):
    if self.last_update and self.brain:
      dt = time.time() - self.last_update

      for mob in list(self.creeps):
        if mob.hp <= 0:
          self.creeps.remove(mob)
          self.dead_creeps.append(mob)
          if mob.killer:
            Global.face.score += int(mob.worth)
            Global.face.mana += mob.worth
        mob.update()

      for tower in list(self.towers):
        tower.update()

      for projectile in list(self.projectiles):
        projectile.update()

      if Global.face.game_over:
        return

      if self.monster_timer > 0:
        self.monster_timer -= dt
      elif self.pools and self.pools[0].creeps:
        monster = Monster(self.pools[0].get_next(), self)
        self.spawn(monster)
        if self.pools[0].boss:
          self.monster_timer = 1.5
        else:
          self.monster_timer = 0.2
      elif len(self.pools) > 1 and self.pools[1].creeps:
        del self.pools[0]
        monster = Monster(self.pools[0].get_next(), self)
        self.spawn(monster)
        self.monster_timer = 3
      elif not self.creeps:
        if self.pools and self.pools[0].boss:
          Global.face.items += 1
        self.monster_timer = 5
        if self.level.level_number > 0:
          Global.face.score += 100
        self.pools = self.level.clone_pools()
#        self.pools = self.level.get_monsters_of_next_level()
        self.genepool_info = "\n\n".join((("\n".join(mob.gene for mob in pool.creeps)) for pool in self.pools))
        self.dead_creeps = list()
        Global.yume.log("Wave number %d will spawn in %d seconds!" % (self.level.level_number, self.monster_timer))

    self.last_update = time.time()

  def draw(self, screen):
    screen.blit(self.background.surface, (0, 0))
    self.bg_tick += 1
    if self.bg_tick >= 3:
      self.background.next_frame()
      self.bg_tick = 0
    if Global.face.dragging:
      if Global.face.dragging == TowerNode:
        self.draw_node_info(screen)
      screen.blit(self.grid, (ARENA_LEFT_POS, ARENA_TOP_POS))
    screen.blit(self.surface, (0, 0))
    for tower in list(self.towers):
      tower.draw(screen)
    for creep in self.creeps:
      creep.draw(screen)
      creep.draw_hp_bar(screen)
    for projectile in self.projectiles:
      projectile.draw(screen)

  def draw_node_info(self, screen):
    if not self.nodes:
      return
    last_node = self.nodes[-1]
    nodex, nodey = last_node.gridpos
    mousex, mousey = pygame.mouse.get_pos()
    mousex, mousey = self.pos_to_cell(mousex, mousey)
    for x in range(40):
      for y in range(28):
        if self.node_allowed_here(x, y):
          a, b = self.cell_to_pos(x, y)
          intunnel = self.node_path(nodex, nodey, x, y, mousex, mousey)
          color = (0, 0, 50) if intunnel else (0, 50, 0)
          pygame.draw.rect(screen, color, Rect(a, b, 25, 25))

  @cached_method
  def node_path(self, nodex, nodey, cellx, celly, mousex, mousey):
    #      b    /
    #    *----/
    #  a |\ /
    #    |/  dist
    #   / line(x) = m * x + c
    # /
#    print("calculating for %d %d %d %d %d %d" % (nodex, nodey, cellx, celly, mousex, mousey))
    try:
      dx = mousex - nodex
      dy = mousey - nodey

      m = float(dy) / dx
      c = nodey - m * nodex
      a = celly - (m * cellx + c)

      m = float(dx) / dy
      c = nodex - m * nodey
      b = cellx - (m * celly + c)

      h = sqrt((a*a * b*b) / (a*a + b*b))
      if h >= 0.5:
        return False
    except ZeroDivisionError:
      pass
    topleftx = min(nodex, mousex)
    toplefty = min(nodey, mousey)
    bottomrightx = max(nodex, mousex)
    bottomrighty = max(nodey, mousey)
    if cellx >= topleftx and cellx <= bottomrightx and\
        celly >= toplefty and celly <= bottomrighty:
      return True
    return False

  def node_allowed_here(self, x, y):
    if not self.nodes:
      return False
    pos = x, y
    if pos not in self.tower_positions:
      return False
    if self.tower_positions[pos]:
      return False
    node = self.nodes[-1]
    distance = sqrt((node.gridpos[0] - x) ** 2 + (node.gridpos[1] - y) ** 2)
    if distance >= 4.3 or distance <= 1.5:
      return False
    last_node = self.nodes[-1]
    nodex, nodey = last_node.gridpos
    mousex, mousey = x, y
    for x in range(nodex-5, nodex+5):
      for y in range(nodey-5, nodey+5):
        if (x, y) in self.tower_positions:
          if self.node_path(nodex, nodey, x, y, mousex, mousey):
            if (x, y) != (nodex, nodey) and self.tower_positions[(x, y)]:
              return False
    return True

  def spawn(self, mon):
    self.creeps.append(mon)
