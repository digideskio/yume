from yume import *
from yume.gfx import Drawable, TowerBubbleGFX
from pygame import Rect
from pygame.draw import *

class Widget(object):
  def move(self, pos):
    self.pos = pos
    self.x, self.y = pos

class MenuButton(Widget, Drawable):
  transparent = True
  height = 40
  width = 40

  def __init__(self, graphic):
    self.graphic = graphic
    Widget.__init__(self)
    Drawable.__init__(self)
    self.tooltip = ""
    self.action = lambda: None
    self.activation_test = lambda: True

  def draw(self, screen, pos):
    self.x, self.y = pos
    self.x += 8
    self.y += 8
    color = (40, 40, 40) if self.activation_test() else (90, 0, 0)
    rect(screen, (0, 0, 0), Rect(pos[0], pos[1], self.width, self.height), 0)
    rect(screen, color, Rect(pos[0], pos[1], self.width-2, self.height-2), 0)
    Drawable.draw(self, screen)
    self.x -= 8
    self.y -= 8

class Menu(Widget):
  width = 50
  def __init__(self, pos):
    self.height = SCREEN_HEIGHT
    self.move(pos)
    button = TowerButton()
    self.buttons = [button]
    button.move((self.x + 10, 100))

  def draw(self, screen):
#    rect(screen, (50, 50, 50), Rect(self.x + self.width - 30, 0, 25, self.height))
#    rect(screen, (50, 50, 50), Rect(self.x + self.width - 30, 0, 25, self.height))
    for button in self.buttons:
      button.draw(screen)
