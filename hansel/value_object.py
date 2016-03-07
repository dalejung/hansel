from collections import OrderedDict

from six import iteritems, with_metaclass

from earthdragon.typelet import (
    Typelet,
    gather_typelets,
    typelet_repr,
    TypeletMeta,
    inflate,
    InvalidInitInvocation
)
from earthdragon.meta import mro

class IllegalMutation(Exception):
    pass

def init_wrapper(func):
    """ wraps __init__ with locking for immutability """
    def _init(self, *args, **kwargs):
        func.__get__(self)(*args, **kwargs)
        # lock object after running init
        self._hansel_locked = True
    return _init

class ValueObjectMeta(TypeletMeta):
    def __prepare__(name, bases):
        mdict = OrderedDict()
        return mdict

    def __new__(cls, name, bases, dct):
        if bases:# only run on ValueObject subclass
            init = mro(dct, bases, '__init__')

            dct['__init__'] = init_wrapper(init)
        return super(ValueObjectMeta, cls).__new__(cls, name, bases, dct)


class ValueObject(metaclass=ValueObjectMeta):
    _hansel_locked = False

    __repr__ = typelet_repr

    def __setattr__(self, name, value):
        # locking again should be fine. This happens with subclasses
        # calling super().__init__
        bypass = name == '_hansel_locked' and value == True
        if self._hansel_locked and not bypass:
            raise IllegalMutation("ValueObjects are immutable.")
        super().__setattr__(name, value)

    def __init__(self, *args, **kwargs):
        """
        Make use of earthdragon.typelets.inflate.
        """
        inflate(self, args, kwargs, require_all=True)
