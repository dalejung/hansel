from six import iteritems, with_metaclass

from .traits import Trait, gather_traits, trait_repr

class EntityMeta(type):
    def __new__(cls, name, bases, dct):
        if bases:# only run on Entity subclass
            traits = gather_traits(dct, bases)
            dct['_hansel_traits'] = traits
        return super(EntityMeta, cls).__new__(cls, name, bases, dct)

class Entity(metaclass=EntityMeta):
    __repr__ = trait_repr
