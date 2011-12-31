def cached_method(fnc):
  fnc._cache = {}
  def result(self, *args):
    if args in fnc._cache:
      return fnc._cache[args]
    value = fnc(self, *args)
    fnc._cache[args] = value
    return value
  return result
