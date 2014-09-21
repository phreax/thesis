import functools
import collections 

class lazy_property(object):
    '''Decorator. Creates a cached property.'''

    def __init__(self, func):
        self._func = func

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._func(obj)
        setattr(obj, self._func.func_name, value)
        return value

class memoize(object):
    '''Decorator. Caches a function's return value each time it is called.'''
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value
    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__
    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)
