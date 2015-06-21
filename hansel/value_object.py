from six import iteritems, with_metaclass

from .traits import Trait, gather_traits

class IllegalMutation(Exception):
    pass

class MissingInit(Exception):
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
        if bases:# only run on ValueObject subclass
            traits = gather_traits(dct, bases)
            dct['_hansel_traits'] = traits

            init = dct.get('__init__', None)
            if init is None:
                raise MissingInit("ValueObject's must have __init__")

            dct['__init__'] = init_wrapper(init)
        return super(ValueObjectMeta, cls).__new__(cls, name, bases, dct)

class ValueObject(metaclass=ValueObjectMeta):
    _hansel_locked = False

    def __setattr__(self, name, value):
        # locking again should be fine. This happens with subclasses
        # calling super().__init__
        bypass = name == '_hansel_locked' and value == True
        if self._hansel_locked and not bypass:
            raise IllegalMutation("ValueObjects are immutable.")
        super().__setattr__(name, value)
