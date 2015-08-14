import nose.tools as nt

import ast
from asttools import (
    quick_parse,
    ast_source,
    transform,
    coroutine
)


from ..auto import generate_apply_func, APPLY_TEMPLATE

source = """
with mutate.apply:
    self.bob = bob
"""
node = quick_parse(source)


apply_code = generate_apply_func(node, 'some_func')
print(ast_source(apply_code))
