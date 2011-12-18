import os.path
import pygame
import random
import sys
import time
from collections import deque
from pygame.locals import *
from optparse import OptionParser
from math import *
from yume.levels import *
from yume.towers import *
from yume.monsters import *
from yume import *

def main():
  pygame.init()
  pygame.font.init()
  if sys.version_info[0] == 3 or sys.version_info[1] <= 5:
    version = sys.version.split()[0]
    print("Python %s not supported.  Need Python >=2.6 <3.0." % version)
    sys.exit(1)

  return Yume().run()

class Yume(object):
  def __init__(self):
    from yume.interface import Images
    Global.yume = self
    Global.images = Images()
    self.log_entries = deque(maxlen=10)

  def log(self, text):
    self.log_entries.appendleft(text)

  def run(self):
    from yume.interface import Interface
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA, 32)
    pygame.display.set_caption('Yume Tower Defense')

    self.interface = Interface()
    Global.face = self.interface

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
          self.interface.click(event.pos, event.button)
        elif event.type is MOUSEBUTTONUP:
          pass

      self.screen.fill((0, 0, 0))
      self.interface.update()
      self.interface.draw(self.screen)
      pygame.display.flip()
