from yume import gfx
from yume import *
import time

class Item(object):
  graphic = gfx.AdrenalinePillGFX
  duration = 30.0
  name = "<unknown substance>"

  def __init__(self, interface):
    self.interface = interface
    self.start_time = time.time()
    self.time_left = self.duration

  def update(self, dt):
    self.time_left = self.duration + (self.start_time - time.time())

  def destroy(self):
    Global.yume.log("%s has worn off." % self.name)
    pass


class AdrenalinePill(Item):
  graphic = gfx.AdrenalinePillGFX
  total_adren_increase = 100.0
  total_adren_max_increase = 10.0
  name = "Adrenaline Pill"

  def update(self, dt):
    Item.update(self, dt)
    self.interface.adren += dt * self.total_adren_increase / self.duration
    self.interface.check_for_death()
    self.interface.adren_max += dt * self.total_adren_max_increase / self.duration


class ManaPotion(Item):
  graphic = gfx.ManaPotionGFX
  name = "Mana Potion"
  total_mana_increase = 120
  duration = 15.0

  def update(self, dt):
    Item.update(self, dt)
    self.interface.mana += dt * self.total_mana_increase / self.duration


class SedativePill(Item):
  graphic = gfx.SedativePillGFX
  name = "Sedative"
  total_adren_decrease = 135
  duration = 90.0

  def update(self, dt):
    Item.update(self, dt)
    self.interface.adren -= dt * self.total_adren_decrease / self.duration
    self.interface.adren_baseline -= dt * self.total_adren_decrease / self.duration
