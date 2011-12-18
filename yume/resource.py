import pygame
import os
from yume.gfx import draw_gfx

FONT_NAME = None
FONT_SIZE = 20

_font_cache = {}
_image_cache = {}
_gfx_cache = {}

def get_font(size=FONT_SIZE):
  if size not in _font_cache:
    _font_cache[size] = pygame.font.Font(FONT_NAME, size)
  return _font_cache[size]

def get_gfx(name, args):
  key = (name, args)
  if key not in _gfx_cache:
    result = draw_gfx(name, args)
    _gfx_cache[key] = result
    return result
  return _gfx_cache[key]

def load_image(name):
  if name in _image_cache:
    return _image_cache[name]
  else:
    fullname = os.path.join(os.path.dirname(__file__), 'graphics', name)
    try:
      image = pygame.image.load(fullname)
    except pygame.error, message:
      print('Cannot load image:', fullname)
      raise SystemExit, message
    image = image.convert_alpha()
    #if colorkey is not None:
      #if colorkey is -1:
        #colorkey = image.get_at((0,0))
        #image.set_colorkey(colorkey, RLEACCEL)
    _image_cache[name] = image
    return image

def get_sprite(name, dirty=False):
  if dirty:
    sprite = pygame.sprite.DirtySprite()
  else:
    sprite = pygame.sprite.Sprite()
  sprite.image = load_image(name)
  sprite.rect = sprite.image.get_rect()
  return sprite
