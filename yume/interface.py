import os
import pygame
import time
from pygame.locals import *
from yume.levels import *
from yume.towers import *
from yume import *

class Images(object):
  def __init__(self):
    self._db = {}

  def load(self, name):
    if name in self._db:
      return self._db[name]
    else:
      image = self.load_image(name)
      self._db[name] = image
      return image

  def make_sprite(self, name):
    sprite = pygame.sprite.Sprite()
    sprite.image = self.load(name)
    sprite.rect = sprite.image.get_rect()
    return sprite

  def load_image(self, name, colorkey=None):
    fullname = os.path.join(os.path.dirname(__file__), 'graphics', name)
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

class Interface(object):
  def __init__(self):
    self.mana_max = 100.0
    self.mana = self.mana_max
    self.mana_regen = 0.1
    self.dragging = None
    self.dragging_sprite = Dragger()
    self.arena = Arena()
    Global.arena = self.arena
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

  def distance_between(self, x1, y1, x2, y2):
    return sqrt((x1-x2) ** 2 + (y1-y2) ** 2)

  def get_monsters_in_range(self, x1, y1, rnge):
    for monster in self.arena.mobrenderer:
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
    self.bottom1.rect.bottomleft = 0, h
    self.bottom2.rect.bottomleft = 500, h
    self.bottom3.rect.bottomleft = 1000, h
    manapos = self.manabar.rect.width / self.mana_max * self.mana - self.manabar.rect.width
    current_manapos = self.manabar.rect.x
    diff = current_manapos - manapos
    if abs(diff) > 2:
      manapos += diff * 0.80
    self.manabar.rect.topleft = manapos, 2
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
    y = ARENA_TOP_POS + self.arena.delay * 10
    for wave in self.arena.level.waves:
      if y > ARENA_HEIGHT:
        break
      rect = pygame.Rect((0, y), (20, 20))
      pygame.draw.rect(screen, (100, 0, 100), rect)
      y += max(25, wave.delay * 10)

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
            Global.yume.log("Not enough mana!" + str(random.randint(1,10)))
    if self.dragging:
      self.undrag()

  def undrag(self):
    self.dragging = None
    self.renderer.remove(self.dragging_sprite)

  def press(self, key):
    if key == K_1:
      self.drag(TowerPrototype)

  def drag(self, obj):
    self.dragging_sprite.change_image(Global.images.load(obj.imagefile))
    self.renderer.add(self.dragging_sprite)
    self.dragging = obj

class Arena(object):
  def __init__(self):
    self.mobsurface = pygame.Surface((ARENA_WIDTH, ARENA_HEIGHT))
    self.mobsurface.set_colorkey((0, 0, 0))
    self.mobsurface = self.mobsurface.convert()
    self.mobrenderer = pygame.sprite.RenderPlain([])
    self.projectiles = set()
    self.rect = pygame.Rect(ARENA_LEFT_POS, ARENA_TOP_POS,
        ARENA_LEFT_POS + ARENA_WIDTH, ARENA_TOP_POS + ARENA_HEIGHT)
    self.renderer = pygame.sprite.RenderPlain([])
    self.load_level(LevelInvocation)

  def load_level(self, cls):
    self.level = cls()
    self.level.initialize()
    Global.level = self.level
    self.last_update = 0
    self.active_waves = set()
    self.delay = 1
    self.towers = []
    self.cells = [[1] * CELLS_X for _ in range(CELLS_Y)]

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
    if self.last_update:
      dt = time.time() - self.last_update

      for mob in list(self.mobrenderer):
        if mob.hp <= 0:
          self.mobrenderer.remove(mob)
          if mob.killer:
            Global.yume.interface.mana += mob.worth

      self.mobrenderer.update()
      for projectile in list(self.projectiles):
        projectile.update()

      for wave in list(self.active_waves):
        if wave.monster_queue:
          wave.monster_tick -= dt
          if wave.monster_tick < 0:
            monster = wave.monster_queue.pop()
            self.spawn(monster)
            wave.monster_tick = wave.monster_delay 

      self.delay -= dt
      if self.level.waves and self.delay < 0:
        wave = self.level.waves.popleft()
        wave.engage()
        self.active_waves.add(wave)
        self.delay = wave.delay

    self.last_update = time.time()

  def draw(self, screen):
    self.level.draw(screen)
    self.mobsurface.fill((0, 0, 0))
    self.mobrenderer.draw(self.mobsurface)
    for projectile in self.projectiles:
      projectile.draw(self.mobsurface)
    screen.blit(self.mobsurface, (ARENA_LEFT_POS, ARENA_TOP_POS))
    self.renderer.draw(screen)
    self.level.draw_above(screen)

  def spawn(self, monster):
    mon = monster()
    mon.x, mon.y = self.level.waypoints_scaled[0]
    mon.waypoints = self.level.waypoints_scaled
    self.mobrenderer.add(mon)

class Dragger(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)

  def change_image(self, image):
    self.image = image
    self.rect = image.get_rect()

  def update(self):
    self.rect.center = pygame.mouse.get_pos()

class Bottom(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = Global.images.load('foot.png')
    self.rect = self.image.get_rect()
