import os
import pygame
import random
import sys
from pygame.locals import *
from optparse import OptionParser
from math import *

class Global(object):
  pass

def main():
  pygame.init()
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

class Interface(object):
  def __init__(self):
    self.bottom1 = Bottom()
    self.bottom2 = Bottom()
    self.bottom3 = Bottom()
    self.container = [self.bottom1, self.bottom2, self.bottom3]
    self.renderer = pygame.sprite.RenderPlain(self.container)

  def draw(self, screen):
    w,h = screen.get_size()
    self.bottom1.rect.bottomleft = 0, h
    self.bottom2.rect.bottomleft = 500, h
    self.bottom3.rect.bottomleft = 1000, h
    self.renderer.update()
    self.renderer.draw(screen)

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

class Yume(object):
  def __init__(self):
    Global.yume = self
    Global.images = Images()

  def run(self):
    self.screen = pygame.display.set_mode((1024, 768), pygame.SRCALPHA, 32)
    pygame.display.set_caption('Yume Tower Defense')

    self.background = pygame.Surface(self.screen.get_size()).convert()
    self.background.fill((0, 0, 0))

    self.interface = Interface()
    moblist = []
    for i in range(1000):
      lame = Lame()
      moblist.append(lame)
    mobs = pygame.sprite.RenderPlain(moblist)

    clock = pygame.time.Clock()
    while True:
      clock.tick(60)
      print(clock.get_fps())

      for event in pygame.event.get():
        if event.type == QUIT:
          return
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE or event.key == K_q:
            return
          elif event.key == K_F11:
            pygame.display.toggle_fullscreen()
        elif event.type == MOUSEBUTTONDOWN:
          pass
        elif event.type is MOUSEBUTTONUP:
          pass

      self.screen.blit(self.background, (0, 0))
      mobs.update()
      mobs.draw(self.screen)
      self.interface.draw(self.screen)
      pygame.display.flip()
