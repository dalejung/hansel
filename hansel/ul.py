from .context_util import WithScope

class UL(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, func):
        """ use for func decorator? """
        return func
