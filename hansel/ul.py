"""
The ubiquitous language module. Basically tools to allow defining a UL, which
is essentially name => validator that can be applied to method params and
varialbe names.

Originally the idea was to make this a Service specific feature, but in reality
a UL instance should be able to wrap arbitrary class / methods
"""
import ast
import types
from asttools import (
    is_load_name,
    quick_parse,
    get_source,
    transform,
    coroutine
)

from hansel.traits import Dict, Trait

from .context_util import WithScope

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

class ULValidator:
    def __init__(self, name, checker):
        self.name = name
        self.checker = checker

    def __or__(self, other):
        checker = self.checker
        if isinstance(checker, Trait):
            return checker.validate(other)
        return checker(other)

def name_to_ulc(name):
    return quick_parse("_ulc.{name}", name=name).value


@coroutine.wrap
def ul_name_transform(ul):
    """
    Transform names that contain
    bob = frank -> _ulc.bob = frank
    """
    used = set()
    node, meta = yield

    def _need_rename(node):
        if node.id in used: # already used before
            return True

        if not is_load_name(node) and node.id in ul:
            return True

        return False

    while True:

        if not isinstance(node, ast.Name) or not _need_rename(node):
            node, meta = yield node
            continue

        used.add(node.id)
        node, meta = yield ast.copy_location(name_to_ulc(node.id), node)
