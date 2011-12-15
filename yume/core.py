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

class Lame(Monster):
  def __init__(self):
    Monster.__init__(self)
    self.image = Global.images.load('enemy-1-pain.png')
    self.rect = self.image.get_rect()
    self.x = random.randint(100, 800)
    self.y = random.randint(50, 800)
    self.t = random.randint(0, 20)

  def update(self):
    self.t += pi / 20
    self.y += cos(self.t)
    self.x += 2 + sin(self.t)
    self.rect.center = (self.x, self.y)

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
    self.container = [self.bottom1, self.bottom2, self.bottom3, self.manabar,
        self.menubar]
    self.renderer = pygame.sprite.RenderPlain(self.container)
    self.last_update = time.time()
    self.font = pygame.font.Font(None, 20)

  def update(self):
    dt = time.time() - self.last_update
    self.last_update = time.time()
    self.mana = max(0, min(self.mana + self.mana_regen * dt, self.mana_max))

  def draw(self, screen):
    w,h = screen.get_size()
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

  def press(self, key):
    if key == K_1:
      self.drag(TowerPrototype)

  def drag(self, obj):
    self.dragging_sprite.change_image(Global.images.load(obj.imagefile))
    self.renderer.add(self.dragging_sprite)
    self.dragging = obj

class Level(object):
  def __init__(self):
    self.waypoints = [(10, 0), (10, 4), (3, 4), (3, 8), (12, 8), (12, 16),
        (6, 16), (6, 21), (18, 21), (18, 8), (32, 8)]

  def initialize(self):
    self.surface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
#    self.surface_red = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
#    self.surface_green = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
#    self.surface_blue = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
#    self.surfaces = [self.surface_red, self.surface_green, self.surface_blue]
#    colors = [(200, 0, 0), (0, 200, 0), (0, 0, 200)]

    def mult(pair):
      return (pair[0] * 25, pair[1] * 25)

#    pygame.draw.lines(self, (0, 255, 0), False, map(mult, self.waypoints), 25)

    t1 = time.time()
#    for surface in self.surfaces:
#      surface.lock()
#      surface.fill((0, 0, 0))
    self.surface.lock()
    self.surface.fill((0, 0, 0))
    for wp in self.waypoints:
      wp_m = (wp[0] * 25 + 1, wp[1] * 25 + 1)
#      for i, surface in enumerate(self.surfaces):
#        pygame.draw.circle(surface, colors[i], wp_m, 12, 0)
#        pygame.draw.circle(surface, (0, 0, 0), wp_m, 11, 0)
      pygame.draw.circle(self.surface, (0, 255, 0), wp_m, 12, 0)
      pygame.draw.circle(self.surface, (0, 0, 0), wp_m, 11, 0)
#    for i, surface in enumerate(self.surfaces):
#      pygame.draw.lines(surface, colors[i], False, map(mult, self.waypoints), 24)
#      pygame.draw.lines(surface, (0, 0, 0), False, map(mult, self.waypoints), 22)
    pygame.draw.lines(self.surface, (0, 255, 0), False, map(mult, self.waypoints), 24)
    pygame.draw.lines(self.surface, (0, 0, 0), False, map(mult, self.waypoints), 22)
    self.surface.unlock()
    self.surface = self.surface.convert()
#    self.surfaces = [surface.convert() for surface in self.surfaces]
#    self.surface_red, self.surface_green, self.surface_blue = self.surfaces
    Global.yume.log("A : " + str(time.time() - t1))

  def update(self):
    pass

  def draw(self, screen):
    screen.blit(self.surface, (ARENA_LEFT_POS, ARENA_TOP_POS))
#    screen.blit(self.surface_red, (ARENA_LEFT_POS, ARENA_TOP_POS))
#    screen.blit(self.surface_green, (ARENA_LEFT_POS, ARENA_TOP_POS))
#    screen.blit(self.surface_blue, (ARENA_LEFT_POS, ARENA_TOP_POS))

  def draw_above(self, screen):
    pass

class Arena(object):
  def __init__(self):
    self.towers = []
    self.rect = pygame.Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self.renderer = pygame.sprite.RenderPlain([])
    self.level = Level()
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
    mobs = pygame.sprite.RenderPlain(moblist)

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
      mobs.update()
      mobs.draw(self.screen)
      pygame.display.flip()
      if i == 0:
        self.log("B : " + str(time.time() - t1))
