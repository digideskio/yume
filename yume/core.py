import os.path
import pygame
import random
import re
import sys
import time
import yume
from collections import deque
from pygame.locals import *
from optparse import OptionParser
from math import *
from yume.levels import *
from yume.towers import *
from yume.resource import *
from yume.monsters import *
from yume import *

def main():
  pygame.init()
  pygame.font.init()
  if sys.version_info[0] == 3 or sys.version_info[1] <= 5:
    version = sys.version.split()[0]
    print("Python %s not supported.  Need Python >=2.6 <3.0." % version)
    sys.exit(1)

  yu = Yume()
  yu.parse_args()
  if yu.profile:
    import cProfile
    import pstats
    exit_code = cProfile.run('yume.Global.yume.run()', 'profile')
    p = pstats.Stats('profile')
    print(p.sort_stats('cumulative').print_stats(100))
  else:
    return yu.run()

class Yume(object):
  def __init__(self):
    Global.yume = self
    self.log_entries = deque(maxlen=10)
    self.profile = False
    self.interface = None

  def log(self, text):
    self.log_entries.appendleft(text)
#    if self.interface is not None:
#      self.interface.draw_console(self.screen)
#      pygame.display.flip()

  def parse_args(self):
    p = OptionParser(usage="%prog [options]")
    p.add_option('-r', '--resolution', type='string')
    p.add_option('-f', '--fullscreen', action='store_true')
    p.add_option('-t', '--test', action='store_true', help="activate test mode")
    p.add_option('-p', '--profile', action='store_true')
    options, _ = p.parse_args()

    if options.resolution:
      match = re.match(r'(\d+)x(\d+)', options.resolution)
      if match:
        w, h = match.groups()
        yume.SCREEN_WIDTH, yume.SCREEN_HEIGHT = int(w), int(h)
    self.profile = bool(options.profile)
    self.fullscreen = bool(options.fullscreen)
    self.test_mode = bool(options.test)

  def run(self):
    from yume.interface import Interface
    flags = pygame.SRCALPHA | pygame.DOUBLEBUF
    if self.fullscreen:
      flags |= pygame.FULLSCREEN
    self.screen = pygame.display.set_mode((yume.SCREEN_WIDTH, yume.SCREEN_HEIGHT),
        flags, 32)
    self.layer = pygame.Surface((yume.ARENA_WIDTH, yume.ARENA_HEIGHT))
    pygame.display.set_caption('Yume Tower Defense')

    self.interface = Interface()
    Global.face = self.interface

    self.clock = pygame.time.Clock()
    i = 0
    while True:
      self.clock.tick(60)
      i += 1
      if i == 180:
        i = 0

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

      self.interface.update()
      if self.layer.get_size() != self.screen.get_size():
        self.interface.draw(self.layer)
        pygame.transform.scale(self.layer, self.screen.get_size(), self.screen)
      else:
        self.interface.draw(self.screen)
      pygame.display.flip()
