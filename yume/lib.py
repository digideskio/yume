def cached_method(fnc):
  cache = {}
  def result(self, *args):
    if args in cache:
      return cache[args]
    value = fnc(self, *args)
    cache[args] = value
    return value
  result._cache = cache
  return result

class OpenStruct(dict):
  def __init__(self, *args, **kws):
    dict.__init__(self, *args, **kws)
    self.__dict__ = self
