import ast

from asttools import (
    Matcher,
    delete_node,
    quick_parse,
    graph_walk,
    ast_source,
    transform,
    coroutine
)
from asttools.function import (
    get_source,
    create_function,
    func_args_realizer,
    func_def_args
)
from earthdragon.feature import Attr
from earthdragon.navel import mutate
from earthdragon.func_util import get_invoked_args

matcher = Matcher('with mutate.apply: _any_')

APPLY_TEMPLATE = """
def {func_name}(self, event):
    assert getattr(event, '__event_type__') == '{func_name}'
"""

PRE_TEMPLATE = """
from hansel.event_sourcing.auto import AutoDomainEvent;
__evt = AutoDomainEvent('{func_name}', **dict({items_list}))
"""

EVENT_TEMPLATE = """
self.publish(__evt)
"""

class EventCaller:
    """
    For now, this is just a wrapper to also store the apply_func. This should
    live somewhere else eventually.
    """
    def __init__(self, func, apply_func):
        self.func = func
        self.apply_func = apply_func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

def auto_wrapper(func):
    new_func, apply_func = mutate_transform(func)
    caller = EventCaller(new_func, apply_func)
    return caller

class ApplyMagic:
    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

class EventSourcer:
    @Attr
    def __init__(self):
        self._events = []
    __init__.add_transform(auto_wrapper)

    def publish(self, event):
        self._events.append(event)
        # for now, immediately apply
        self.apply(event)

    @mutate
    def apply(self, event):
        event_type = event.__event_type__
        apply_func = getattr(self, event_type).decorator.func.apply_func
        if apply_func:
            return apply_func(self, event)

    @classmethod
    def load_from_history(cls, events):
        obj = cls.__new__(cls)
        for event in events:
            obj.apply(event)
        return obj

def _template_lines(template, **kwargs):
    if not template:
        return []

    formatted = template.format(**kwargs)
    return ast.parse(formatted).body

def replace_with_block(parent, field_name, field_index):
    """
    add in event handling to replace with mutatae.apply: statement
    ```
    with mutate.apply:
        self.bob = 1
    ```
    turns into
    ```
    self.publish(__evt)
    """
    field_list = getattr(parent, field_name)
    assert isinstance(field_list, list)
    event_lines = _template_lines(EVENT_TEMPLATE)
    event_added = field_list[:field_index] + event_lines + field_list[field_index:]
    setattr(parent, field_name, event_added)


def _split_apply(code):
    """
    Split the apply portion of a method from its event source apply
    """
    func_def = code.body[0]
    assert isinstance(func_def, ast.FunctionDef), "input should be module with single function def"
    apply_code = None
    args = func_def_args(func_def)
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
            apply_code = generate_apply_code(node, func_def)
            break
    else:
        event_lines = _template_lines(EVENT_TEMPLATE)
        func_def.body = func_def.body + event_lines

    # add the event prep lines. this is done backwards
    # because replace_with_block needs the correct field_index of
    # the with mutate.apply block
    items_list = func_args_realizer(args)
    pre_lines = _template_lines(PRE_TEMPLATE,
                            func_name=func_def.name,
                            items_list=items_list)
    func_def.body = pre_lines + func_def.body

    return code, apply_code

@coroutine.wrap
def expose_event(args):
    """
    change free vars to instead grab from event object
    `bob = frank` -> `bob = event.frank`
    """
    node, meta = yield

    while True:

        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) \
           and node.id != 'self' and node.id in args:
            new_node = quick_parse("event.{name}", name=node.id).value
            node, meta = yield new_node
            continue
        node, meta = yield node
        continue

def generate_apply_code(node, func_def):
    """
    Takes the `with mutate.apply:` and turns it into a function that will
    accept a domain event and mutate the state.

    A simple heuristic is that it will replace any non `self` free var
    with `event.{var}`. this means that actual apply logic should be super
    simple and realistically only rely on the domain event info.

    This is likely a limiting approach, so it's possible the logic will get
    more complicated to afford more flexibility.
    """
    func_name = func_def.name
    args = func_def_args(func_def)
    apply_code = quick_parse(APPLY_TEMPLATE, func_name=func_name)
    new_body = transform(node, expose_event(args))
    apply_code.body = apply_code.body + new_body.body
    return apply_code

def mutate_transform(func):
    func_name = func.__name__
    source = get_source(func)
    code = ast.parse(source)
    code, apply_code = _split_apply(code)
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

class AutoDomainEvent:
    __slots__ = ('__event_type__', '__dict__')
    def __init__(self, __event_type, **kwargs):
        self.__event_type__ = __event_type
        self.__dict__.update(kwargs)

    def __repr__(self):
        msg = "AutoDomainEvent({event_type}, {data}".format
        return msg(event_type=self.__event_type__, data=repr(self.__dict__))
