class Global(object):
  pass

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
ARENA_LEFT_POS = 30
ARENA_TOP_POS = 20
ARENA_WIDTH = 1024
ARENA_HEIGHT = 768
CELL_WIDTH = 25
CELL_HEIGHT = 25
CELLS_X = ARENA_WIDTH / CELL_WIDTH
CELLS_Y = ARENA_HEIGHT / CELL_HEIGHT

STATUS_TEMPLATE = """score: {score}
level: {level}
mana: {mana}
hits/shots = {hits}/{shots}
aiming = {hitpercent}%
adrenaline: {adrenaline}/{adrenalinemax}
items available: {items}
FPS: {fps}

Gene Pool:
{genepool}"""
