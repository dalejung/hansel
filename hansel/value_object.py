from collections import OrderedDict

from six import iteritems, with_metaclass

from .traits import Trait, gather_traits, trait_repr
from .meta import mro

class IllegalMutation(Exception):
    pass

class InvalidInitInvocation(Exception):
    pass

def init_wrapper(func):
    """ wraps __init__ with locking for immutability """
    def _init(self, *args, **kwargs):
        func.__get__(self)(*args, **kwargs)
        # lock object after running init
        self._hansel_locked = True
    return _init

class ValueObjectMeta(type):
    def __prepare__(name, bases):
        mdict = OrderedDict()
        return mdict

    def __new__(cls, name, bases, dct):
        if bases:# only run on ValueObject subclass
            traits = gather_traits(dct, bases)
            dct['_hansel_traits'] = traits

            init = mro(dct, bases, '__init__')

            dct['__init__'] = init_wrapper(init)
        return super(ValueObjectMeta, cls).__new__(cls, name, bases, dct)

def fill(obj, filled, name, value):
    if name in filled:
        raise InvalidInitInovation("Error")
    setattr(obj, name, value)
    filled[name] = True

class ValueObject(metaclass=ValueObjectMeta):
    _hansel_locked = False

    __repr__ = trait_repr

    def __setattr__(self, name, value):
        # locking again should be fine. This happens with subclasses
        # calling super().__init__
        bypass = name == '_hansel_locked' and value == True
        if self._hansel_locked and not bypass:
            raise IllegalMutation("ValueObjects are immutable.")
        super().__setattr__(name, value)

    def __init__(self, *args, **kwargs):
        """
        Default __init__. Requires that hansel_traits be specified.
        """
        filled = {}
        _traits = self._hansel_traits

        if len(args) > len(_traits):
            raise InvalidInitInvocation("Passed too many positional values")

        if not set(kwargs).issubset(_traits):
            raise InvalidInitInvocation("Pass non trait keyword arg")

        for arg, name in zip(args, _traits):
            fill(self, filled, name, arg)

        for k, v in kwargs.items():
            fill(self, filled, k, v)

        if set(filled) != set(_traits):
            raise InvalidInitInvocation("Need to fill all args")
