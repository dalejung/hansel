import inspect
import ast
import astor
from six import iteritems, with_metaclass
from functools import wraps
from earthdragon.classy import mix, MixinMeta

from asttools import graph_walk, Matcher, delete_node, quick_parse
from asttools.function import (
    get_invoked_args,
    get_source,
    create_function,
    func_args_realizer
)

from earthdragon.typelet import Typelet, gather_typelets, typelet_repr

class UnexpectedMutationError(Exception):
    pass


class EntityMeta(MixinMeta):
    def __new__(cls, name, bases, dct):
        if bases:
            typelets = gather_typelets(dct, bases)
            dct['_hansel_typelets'] = typelets
            # wrap all inits with unlocking
            init = dct.get('__init__', None)
            if init:
                dct['__init__'] = Lockable.unlock(init)
        return super(EntityMeta, cls).__new__(cls, name, bases, dct)


class Entity(metaclass=EntityMeta):
    __repr__ = typelet_repr


class Lockable:
    _entity_locked = False

    def __setattr__(self, name, value):
        if name in ['_entity_locked']:
            return super().__setattr__(name, value)

        if self._entity_locked:
            raise UnexpectedMutationError()
        return super().__setattr__(name, value)

    @staticmethod
    def unlock(func):
        @wraps(func)
        def _wrap(self, *args, **kwargs):
            self._entity_locked = False
            res = func(self, *args, **kwargs)
            self._entity_locked = True
            return res
        return _wrap


mix(Entity, Lockable)

class MutateMagic:
    def __init__(self):
        self.wrappers = []

    def add_wrapper(self, wrapper):
        self.wrappers.append(wrapper)

    def __call__(self, func):
        for wrapper in self.wrappers[::-1]:
            func = wrapper(func)
        return func

mutate = MutateMagic()
mutate.add_wrapper(Lockable.unlock)

from .event_sourcing.auto import ApplyMagic, mutate_transform, EventSourcer
mutate.apply = ApplyMagic()
mix(Entity, EventSourcer)

def auto_wrapper(func):
    # wrap init to allow mutataion
    new_func, apply_func = mutate_transform(func)
    new_func.__hansel_mutated = True
    return new_func

mutate.add_wrapper(auto_wrapper)
