import pygame
import random
import time
from collections import deque
from yume.monsters import *
from yume import *

class Level(object):
  def __init__(self, startgene="", pools=1):
    self.gene = startgene

  def mutate(self):
    self.gene += random.sample('abc', 1)[0]

  def get_monsters(self):
    return list(self.gene for _ in range(10))
