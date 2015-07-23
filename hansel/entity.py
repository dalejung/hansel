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
    new_func, apply_func = mutate.transform(init)

    @wraps(new_func)
    def _init(self, *args, **kwargs):
        self._events = []
        new_func(self, *args, **kwargs)
    return mutate.unlock(_init, apply_func)


class Entity(metaclass=EntityMeta):
    __repr__ = trait_repr

    def publish(self, event):
        self._events.append(event)

    def __setattr__(self, name, value):
        if name in ['_entity_lock']:
            return super().__setattr__(name, value)

        if not self._entity_lock:
            raise UnexpectedMutationError()
        return super().__setattr__(name, value)

matcher = Matcher('with mutate.apply: _any_')

APPLY_TEMPLATE = """
def {func_name}(self, event):
    assert event.__event_type == {func_name}
    locals().update(event.__dict__)
"""

PRE_TEMPLATE = """
from hansel.entity import AutoDomainEvent;
__evt = AutoDomainEvent('{func_name}', **dict({items_list}))
"""

EVENT_TEMPLATE = """
self.publish(__evt)
"""

def code_lines(template, **kwargs):
    if not template:
        return []

    formatted = template.format(**kwargs)
    return ast.parse(formatted).body

def decorate_code(template, **kwargs):
    bits = template.split('{code}')
    pre_lines = code_lines(bits[0], **kwargs)

    post_lines = []
    if len(bits) > 1:
        post_lines = code_lines(bits[1], **kwargs)
    return pre_lines, post_lines


def replace_with_block(parent, field_name, field_index):
    # add in event handling to replace with mutatae.apply: statement
    field_list = getattr(parent, field_name)
    assert isinstance(field_list, list)
    event_lines = code_lines(EVENT_TEMPLATE)
    event_added = field_list[:field_index] + event_lines + field_list[field_index:]
    setattr(parent, field_name, event_added)


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
        parent = item['parent']
        field_name = item['field_name']
        field_index = item['field_index']

        if matcher.match(node):
            # remove with statement and replace with event handling
            delete_node(parent, field_name, field_index, node)
            replace_with_block(parent, field_name, field_index)

            # extract the apply code that mutates state
            apply_code = quick_parse(APPLY_TEMPLATE, func_name=func_def.name)
            apply_code.body = apply_code.body + node.body
            break
    else:
        event_lines = code_lines(EVENT_TEMPLATE)
        func_def.body = func_def.body + event_lines

    # add the event prep lines. this is done backwards
    # because replace_with_block needs the correct field_index of
    # the with mutate.apply block
    items_list = func_args_realizer(func_def)
    pre_lines = code_lines(PRE_TEMPLATE,
                            func_name=func_def.name,
                            items_list=items_list)
    func_def.body = pre_lines + func_def.body

    return code, apply_code

class MutateMagic:
    def __init__(self):
        self.apply = ApplyMagic()

    def __call__(self, func):
        new_func, apply_func = self.transform(func)
        return self.unlock(new_func, apply_func)

    def unlock(self, func, apply_func):
        @wraps(func)
        def _wrap(self, *args, **kwargs):
            self._entity_lock = True
            res = func(self, *args, **kwargs)
            self._entity_lock = False
            return res
        _wrap.__hansel_mutated__ = True
        return _wrap

    def transform(self, func):
        if getattr(func, '__hansel_mutated__', False):
            raise Exception('Already wrapped')
        func_name = func.__name__
        source = get_source(func)
        code = ast.parse(source)
        code, apply_code = split_apply(code)
        new_func = create_function(code, func)
        apply_func = None
        if apply_code:
            apply_func = create_function(apply_code, func)

        # don't lose previous function wrapper
        # get_source will grab source of original function
        if hasattr(func, '__wrapped__'):
            func.__wrapped__ = new_func
        else:
            func = new_func
        return func, apply_func

class ApplyMagic:
    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

mutate = MutateMagic()

class AutoDomainEvent:
    __slots__ = ('__event_type', '__dict__')
    def __init__(self, __event_type, **kwargs):
        self.__event_type = __event_type
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "AutoDomainEvent({event_type}, {data}".format(event_type=self.__event_type, data=repr(self.__dict__))
