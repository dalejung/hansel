"""
The ubiquitous language module. Basically tools to allow defining a UL, which
is essentially name => validator that can be applied to method params and
varialbe names.

Originally the idea was to make this a Service specific feature, but in reality
a UL instance should be able to wrap arbitrary class / methods
"""
import ast
import inspect
import types
from asttools import (
    is_load_name,
    quick_parse,
    get_source,
    transform,
    coroutine
)

from hansel.traits import Dict, Trait

from ..context_util import WithScope

class UL(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, func):
        """ use for func decorator? """
        return func

class ULContext:
    _ul = Dict(Trait)

    def __init__(self, _ul, **kwargs):
        self._ul = _ul
        self._cache = {}

    def __setattr__(self, name, value):
        if name in ['_ul', '_cache']:
            return super().__setattr__(name, value)
        raise Exception("Cannot set attribute outside of constructor")

    def __contains__(self, name):
        return name in self._ul

    def __getattr__(self, name):
        if name in self._ul:
            return self._get(name)
        raise AttributeError()

    def _get(self, name):
        checker = self._ul[name]
        if name not in self._cache:
            validator = ULValidator(name, checker)
            self._cache[name] = validator
        return self._cache[name]

    def __dir__(self):
        return self._ul.keys()

class ULValidator:
    def __init__(self, name, checker):
        self.name = name
        self.checker = checker

    def __or__(self, other):
        checker = self.checker
        if isinstance(checker, Trait):
            return checker.validate(other)
        return checker(other)

def add_validate_pipe(value, name):
    binop = quick_parse("_ulc.{name} | True", name=name).value
    binop.right = value
    ast.copy_location(binop, value)
    return binop

@coroutine.wrap
def validation_pipe_transform(ul):
    """
    Transform names that contain
    bob = frank -> bob = _ulc.bob | frank

    If is assumed that the _ulc.bob will validate `frank`.
    """
    used = set()
    node, meta = yield

    while True:

        if not isinstance(node, ast.Assign):
            node, meta = yield node
            continue

        new_value = node.value
        for i, target in enumerate(node.targets):
            if isinstance(target, ast.Name) and target.id in ul:
                new_value = add_validate_pipe(new_value, target.id)
        node.value = new_value
        node, meta = yield node


@coroutine.wrap
def func_validation_transform(ul):
    """
    Transform function definitions from
    def bob(ul_term, random_var):
        return True

    def bob(ul_term, random_var):
        _ulc.ul_term | ul_term
        return True
    """
    used = set()
    node, meta = yield

    while True:

        if not isinstance(node, ast.FunctionDef):
            node, meta = yield node
            continue

        args = list(map(lambda x:x.arg, node.args.args))
        for arg in filter(lambda x: x in ul, args):
            ulc_check = quick_parse("_ulc.{name} | {name}", name=arg)
            node.body.insert(0, ulc_check)

        ulc_load = quick_parse("_ulc = __hansel_ul__.context('{func_name}', id={ulc_id})",
                               func_name=node.name,
                               ulc_id=id(ul))
        node.body.insert(0, ulc_load)
        node, meta = yield node

def ulc_transform(code, ulc):
    # applies the ulc transformations
    transform(code, validation_pipe_transform(ulc))
    transform(code, func_validation_transform(ulc))

def wrap_function(func, ulc):
    """
    Grabs a function, applies UL validation, returns new function
    """
    func_name = func.__name__
    from hansel.ul import __hansel_ul__
    __hansel_ul__.ulc[id(ulc)] = ulc

    code = ast.parse(get_source(func))
    ulc_transform(code, ulc)

    # exec and redfine func in its original namespace
    code_obj = compile(code, inspect.getfile(func), 'exec')
    ns = {}
    func.__globals__['__hansel_ul__'] = __hansel_ul__
    exec(code_obj, func.__globals__, ns)
    new_func = ns[func_name]
    return new_func

def ul_validate(ulc):
    def _wrapper(func):
        return wrap_function(func, ulc)
    return _wrapper

class ULContextManager:

    def __init__(self):
        self.ulc = {}

    def context(self, namespace, id=None):
        # for now ignore namespace
        return self.ulc[id]

__hansel_ul__ = ULContextManager()
