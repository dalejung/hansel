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

from .traits import Trait, gather_traits, trait_repr

class UnexpectedMutationError(Exception):
    pass

class EntityMeta(type):
    def __new__(cls, name, bases, dct):
        if bases:# only run on Entity subclass
            traits = gather_traits(dct, bases)
            dct['_hansel_traits'] = traits
            dct['_entity_lock'] = False
            dct['__apply_funcs__'] = {}
            if '__init__' in dct:
                dct['__init__'] = entity_init(dct['__init__'])
        return super(EntityMeta, cls).__new__(cls, name, bases, dct)

def entity_init(init):
    @wraps(init)
    def _init(self, *args, **kwargs):
        self._events = []
        init(self, *args, **kwargs)
    return mutate(_init)


class Entity(metaclass=EntityMeta):
    __repr__ = trait_repr

    def __setattr__(self, name, value):
        if name in ['_entity_lock']:
            return super().__setattr__(name, value)

        if not self._entity_lock:
            raise UnexpectedMutationError()
        return super().__setattr__(name, value)

matcher = Matcher('with ~apply: _any_')

APPLY_TEMPLATE = """
def {func_name}(self, event):
    assert event.__event_type == {func_name}
    locals().update(event.__dict__)
"""
def split_apply(code):
    """
    Split the apply portion of a method from its event source apply
    """
    func_def = code.body[0]
    assert isinstance(func_def, ast.FunctionDef), "input should be module with single function def"
    apply_code = None
    # find the with apply: block if it exists
    for item in graph_walk(code):
        node = item['node']
        if matcher.match(node):
            items_list = func_args_realizer(func_def)
            evt_string = "from hansel.entity import AutoDomainEvent; __evt = AutoDomainEvent('{func_name}', **dict({items_list}))".format(func_name=func_def.name, items_list=items_list)
            domain_event_node = ast.parse(evt_string)
            delete_node(item['parent'], item['field_name'], item['field_index'], item['node'])
            func_def.body = domain_event_node.body + func_def.body
            apply_code = quick_parse(APPLY_TEMPLATE, func_name=func_def.name)
            apply_code.body = apply_code.body + node.body
            break
    return code, apply_code

class MutateMagic:
    def __call__(self, func):
        if getattr(func, '__hansel_mutated__', False):
            raise Exception('Already wrapped')
        func_name = func.__name__
        source = get_source(func)
        code = ast.parse(source)
        code, apply_code = split_apply(code)
        new_func = create_function(code, func)
        if apply_code:
            apply_func = create_function(apply_code, func)
        # don't lose previous function wrapper
        # get_source will grab source of original function
        if hasattr(func, '__wrapped__'):
            func.__wrapped__ = new_func
        else:
            func = new_func
        @wraps(func)
        def _wrap(self, *args, **kwargs):
            self._entity_lock = True
            res = func(self, *args, **kwargs)
            self._entity_lock = False
            return res
        _wrap.__hansel_mutated__ = True
        return _wrap

class ApplyMagic:
    def __invert__(self):
        return self

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

mutate = MutateMagic()
apply = MutateMagic()

class AutoDomainEvent:
    __slots__ = ('__event_type', '__dict__')
    def __init__(self, __event_type, **kwargs):
        self.__event_type = __event_type
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "AutoDomainEvent({event_type}, {data}".format(event_type=self.__event_type, data=repr(self.__dict__))
