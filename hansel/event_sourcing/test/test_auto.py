import nose.tools as nt

import ast
from asttools import (
    quick_parse,
    ast_source,
    transform,
    coroutine
)


from ..auto import generate_apply_code, APPLY_TEMPLATE

source = """
with mutate.apply:
    self.bob = bob
"""
correct = """
with mutate.apply:
    self.bob = event.bob
"""
node = quick_parse(source)
