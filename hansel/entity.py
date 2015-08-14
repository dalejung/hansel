import inspect
import ast
import astor
from six import iteritems, with_metaclass
from functools import wraps

from asttools import graph_walk, Matcher, delete_node, quick_parse
from asttools.function import (
    get_invoked_args,
    get_source,
    create_function,
    func_args_realizer
)
from earthdragon.navel import (
    Navel,
    NavelMeta,
    mutate,
    features,
    UnexpectedMutationError,
)
from earthdragon.typelet import Typelet, gather_typelets, typelet_repr

class EntityMeta(NavelMeta):
    def __new__(cls, name, bases, dct):
        if bases:
            typelets = gather_typelets(dct, bases)
            dct['_hansel_typelets'] = typelets
        return super(EntityMeta, cls).__new__(cls, name, bases, dct)


class Entity(Navel, metaclass=EntityMeta):
    __repr__ = typelet_repr

from .event_sourcing.auto import ApplyMagic, EventSourcer, auto_wrapper
# entity specific mutate
mutate = mutate.copy()
mutate.apply = ApplyMagic()
mutate.add_transform(auto_wrapper)

features(EventSourcer)(Entity)
