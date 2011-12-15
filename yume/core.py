import os
import pygame
import random
import sys
import time
from collections import deque
from pygame.locals import *
from optparse import OptionParser
from math import *

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
ARENA_LEFT_POS = 30
ARENA_TOP_POS = 20
ARENA_WIDTH = 800
ARENA_HEIGHT = 600
CELL_WIDTH = 25
CELL_HEIGHT = 25
CELLS_X = ARENA_WIDTH / CELL_WIDTH
CELLS_Y = ARENA_HEIGHT / CELL_HEIGHT

def tupleadd(tup1, tup2):
  return [a + b for a, b in zip(tup1, tup2)]

class Global(object):
  pass

def main():
  pygame.init()
  pygame.font.init()
  if sys.version_info[0] == 3 or sys.version_info[1] <= 5:
    version = sys.version.split()[0]
    print("Python %s not supported.  Need Python >=2.6 <3.0." % version)
    sys.exit(1)

  return Yume().run()

def load_image(name, colorkey=None):
    fullname = os.path.join('yume', 'graphics', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print('Cannot load image:', fullname)
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

class Bottom(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = Global.images.load('foot.png')
    self.rect = self.image.get_rect()

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

class Dragger(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)

  def change_image(self, image):
    self.image = image
    self.rect = image.get_rect()

  def update(self):
    self.rect.center = pygame.mouse.get_pos()

class Interface(object):
  def __init__(self):
    self.mana_max = 100.0
    self.mana = self.mana_max
    self.mana_regen = 1
    self.dragging = None
    self.dragging_sprite = Dragger()
    self.arena = Arena()
    self.bottom1 = Bottom()
    self.bottom2 = Bottom()
    self.bottom3 = Bottom()
    self.manabar = Global.images.make_sprite('mana.png')
    self.menubar = Global.images.make_sprite('menu.png')
    self.wave_marker = pygame.Surface((30, ARENA_HEIGHT))
    self.container = [self.bottom1, self.bottom2, self.bottom3, self.manabar,
        self.menubar]
    self.renderer = pygame.sprite.RenderPlain(self.container)
    self.last_update = time.time()
    self.font = pygame.font.Font(None, 20)

  def update(self):
    dt = time.time() - self.last_update
    self.last_update = time.time()
    self.mana = max(0, min(self.mana + self.mana_regen * dt, self.mana_max))

  def crash(self):
    self.mana = int(self.mana * 0.5)

  def draw(self, screen):
    w, h = screen.get_size()
    self.bottom1.rect.bottomleft = 0, h
    self.bottom2.rect.bottomleft = 500, h
    self.bottom3.rect.bottomleft = 1000, h
    manapos = self.manabar.rect.width / self.mana_max * self.mana
    self.manabar.rect.topleft = manapos - self.manabar.rect.width, 2
    self.menubar.rect.topright = w, 0
    self.arena.update()
    self.arena.draw(screen)
    self.renderer.update()
    self.renderer.draw(screen)
    x, y = 0, SCREEN_HEIGHT
    color = 255
    for text in Global.yume.log_entries:
      y -= self.font.get_height() + 2
      text = self.font.render(text, 1, (color, color, color))
      color -= 24
      screen.blit(text, (x, y))
    y = ARENA_TOP_POS + self.arena.level.delay * 10
    for wave in self.arena.level.waves:
      if y > ARENA_HEIGHT:
        break
      rect = pygame.Rect((0, y), (20, 20))
      pygame.draw.rect(screen, (100, 0, 100), rect)
      y += max(25, wave.delay * 10)

  def click(self, pos, button):
    if self.arena.rect.collidepoint(pos):
      if self.dragging:
        if self.mana >= self.dragging.cost:
          released = self.arena.release(self.dragging, pos)
          if released:
            self.mana -= self.dragging.cost
            self.dragging = None
            self.renderer.remove(self.dragging_sprite)
        else:
          Global.yume.log("Not enough mana!" + str(random.randint(1,10)))
    elif button != 2 and self.dragging:
      self.dragging = None
      self.renderer.remove(self.dragging_sprite)

  def press(self, key):
    if key == K_1:
      self.drag(TowerPrototype)

  def drag(self, obj):
    self.dragging_sprite.change_image(Global.images.load(obj.imagefile))
    self.renderer.add(self.dragging_sprite)
    self.dragging = obj

class Level(object):
  def __init__(self):
    self.waves = deque()
    self.waypoints = [(0, 0)]
    self.delay = 1
    self.last_update = 0

  def initialize(self):
    self.mobrenderer = pygame.sprite.RenderPlain([])
    self.cells = [[1] * CELLS_X for _ in range(CELLS_Y)]
    self.remove_wave = 0
    self.active_waves = set()
    self.surface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    self.mobsurface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    self.mobsurface.set_colorkey((0, 0, 0))
    self.mobsurface = self.mobsurface.convert()

    def mult(pair):
      return (pair[0] * 25, pair[1] * 25)

    self.waypoints_scaled = map(mult, self.waypoints)

    t1 = time.time()
    self.surface.lock()
    self.surface.fill((0, 0, 0))
    for wp in self.waypoints:
      wp_m = (wp[0] * CELL_WIDTH + 1, wp[1] * CELL_WIDTH + 1)
      pygame.draw.circle(self.surface, (0, 155, 0), wp_m, 12, 0)
      pygame.draw.circle(self.surface, (0, 0, 0), wp_m, 11, 0)
    pygame.draw.lines(self.surface, (0, 155, 0), False, self.waypoints_scaled, 24)
    pygame.draw.lines(self.surface, (0, 0, 0), False, self.waypoints_scaled, 22)
    self.surface.unlock()
    self.surface = self.surface.convert()

  def update(self):
    if self.last_update:
      dt = time.time() - self.last_update

      for mob in list(self.mobrenderer):
        if mob.hp <= 0:
          self.mobrenderer.remove(mob)
          if mob.killer:
            Global.yume.interface.mana += mob.worth

      self.mobrenderer.update()

      for wave in list(self.active_waves):
        if wave.monster_queue:
          wave.monster_tick -= dt
          if wave.monster_tick < 0:
            monster = wave.monster_queue.pop()
            self.spawn(monster)
            wave.monster_tick = wave.monster_delay 

      self.delay -= dt
      if self.waves and self.delay < 0:
        wave = self.waves.popleft()
        wave.engage()
        self.active_waves.add(wave)
        self.delay = wave.delay

    self.last_update = time.time()

  def spawn(self, monster):
    mon = monster()
    mon.x, mon.y = self.waypoints_scaled[0]
    mon.waypoints = self.waypoints_scaled
    self.mobrenderer.add(mon)

  def draw(self, screen):
    screen.blit(self.surface, (ARENA_LEFT_POS, ARENA_TOP_POS))
    self.mobsurface.fill((0, 0, 0))
    self.mobrenderer.draw(self.mobsurface)
    screen.blit(self.mobsurface, (ARENA_LEFT_POS, ARENA_TOP_POS))

  def draw_above(self, screen):
    pass

class LevelInvocation(Level):
  def __init__(self):
    Level.__init__(self)
    self.waypoints = [(10, 0), (10, 4), (3, 4), (3, 8), (12, 8), (12, 16),
        (6, 16), (6, 21), (18, 21), (18, 8), (32, 8)]
    self.waves = deque([])
    self.waves.append(Wave({Lame: 5}, mps=1, delay=3))
    self.waves.append(Wave({Lame: 10}, mps=10, delay=2))
    self.waves.append(Wave({Lame: 30}, mps=60, delay=2))

class Wave(object):
  def __init__(self, monsters, mps, delay):
    self.monsters = monsters
    self.mps = mps  # monsters per second
    self.delay = delay

  def engage(self):
    add = lambda x, y: x + y
    self.monster_queue = reduce(add,
        [[cls] * n for cls, n in self.monsters.items()])
    random.shuffle(self.monster_queue)
    self.monster_delay = 1 / float(self.mps)
    self.monster_tick = 0

class Arena(object):
  def __init__(self):
    self.towers = []
    self.rect = pygame.Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self.renderer = pygame.sprite.RenderPlain([])
    self.level = LevelInvocation()
    self.level.initialize()

  def release(self, obj, pos):
    if issubclass(obj, Tower):
      self.createTower(obj, pos)
      return True

  def createTower(self, cls, pos):
    tower = cls()
    tower.move(*pos)
    self.towers.append(cls())
    self.renderer.add(tower)

  def update(self):
    self.renderer.update()
    self.level.update()

  def draw(self, screen):
    self.level.draw(screen)
    self.renderer.draw(screen)
    self.level.draw_above(screen)

class Images(object):
  def __init__(self):
    self._db = {}

  def load(self, name):
    if name in self._db:
      return self._db[name]
    else:
      image = load_image(name)
      self._db[name] = image
      return image

  def make_sprite(self, name):
    sprite = pygame.sprite.Sprite()
    sprite.image = self.load(name)
    sprite.rect = sprite.image.get_rect()
    return sprite

class Yume(object):
  def __init__(self):
    Global.yume = self
    Global.images = Images()
    self.log_entries = deque(maxlen=10)

  def log(self, text):
    self.log_entries.appendleft(text)

  def run(self):
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA, 32)
    pygame.display.set_caption('Yume Tower Defense')

    self.interface = Interface()
    moblist = []
#    for i in range(10):
#      lame = Lame()
#      moblist.append(lame)

    clock = pygame.time.Clock()
    i = 0
    while True:
      clock.tick(60)
      i += 1
      if i == 180:
        i = 0
        self.log("%.3f FPS" % clock.get_fps())

      t1 = time.time()
      for event in pygame.event.get():
        if event.type == QUIT:
          return
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE or event.key == K_q:
            return
          elif event.key == K_F11:
            pygame.display.toggle_fullscreen()
          else:
            self.interface.press(event.key)
        elif event.type == MOUSEBUTTONDOWN:
          if event.button == 1:
            self.interface.click(event.pos, event.button)
        elif event.type is MOUSEBUTTONUP:
          pass

      self.screen.fill((0, 0, 0))
      self.interface.update()
      self.interface.draw(self.screen)
      pygame.display.flip()
