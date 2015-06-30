"""
The ubiquitous language module. Basically tools to allow defining a UL, which
is essentially name => validator that can be applied to method params and
varialbe names.

Originally the idea was to make this a Service specific feature, but in reality
a UL instance should be able to wrap arbitrary class / methods
"""
from .context_util import WithScope

class UL(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, func):
        """ use for func decorator? """
        return func
