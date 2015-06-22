import types
from .traits import Trait, gather_traits, trait_repr
from .traits import Int, UUID
from .context_util import WithScope

def wrap_method_func(func, traits):
    # TODO match on trait key names and args and do type checking
    return func

class ServiceMeta(type):
    def __new__(cls, name, bases, dct):
        if bases:# only run on Entity subclass
            traits = gather_traits(dct, bases)
            dct['_hansel_traits'] = traits

            ul_traits = dct.get('_hansel_ul')
            for k, v in dct.items():
                if isinstance(v, types.FunctionType):
                    dct[k] = wrap_method_func(v, ul_traits)

        return super(ServiceMeta, cls).__new__(cls, name, bases, dct)

class Service(metaclass=ServiceMeta):
    @classmethod
    def UL(cls):
        def handler(self, out):
            # add new vars to class dict
            new_vars = out['new_vars']
            self.scope['_hansel_ul'] = new_vars
        return WithScope(exit_handler=handler)
