from six import iteritems, with_metaclass

from .traits import Trait

class IllegalMutation(Exception):
    pass

def init_wrapper(func):
    """ wraps __init__ with locking for immutability """
    def _init(self, *args, **kwargs):
        func.__get__(self)(*args, **kwargs)
        # lock object after running init
        self._hansel_locked = True
    return _init

class ValueObjectMeta(type):
    def __new__(cls, name, bases, dct):
        traits = {}
        for k, v in iteritems(dct):
            if isinstance(v, Trait):
                traits[k] = v

        if bases:# only run on ValueObject subclass
            init = dct.get('__init__', None)
            if init is None:
                raise Exception("ValueObject's must have __init__")

            dct['__init__'] = init_wrapper(init)
        return super(ValueObjectMeta, cls).__new__(cls, name, bases, dct)

class ValueObject(metaclass=ValueObjectMeta):
    _hansel_locked = False

    def __setattr__(self, name, value):
        if self._hansel_locked:
            raise IllegalMutation("ValueObjects are immutable.")
        super().__setattr__(name, value)
