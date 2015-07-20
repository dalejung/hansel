import uuid
import astor
import ast
from asttools import quick_parse, get_source, transform, coroutine

from ..ul import (
    ULContext,
    validation_pipe_transform,
    func_validation_transform,
    UL
)
from hansel.traits import UUID, Int, Type, List

class __hansel_ul__:

    ulc = {}

    @classmethod
    def context(cls, namespace, id=None):
        # for now ignore namespace
        return cls.ulc[id]

class SomeType:
    pass

class Cart:
    line_items = List('LineItem')
    def __init__(self, id):
        self.id = id
        self.line_items = []

    def add_item(self, line_item):
        self.line_items.append(line_item)

class LineItem:
    def __init__(self, cart_id, product_id, quantity):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

def order_item(cart, product_id, quantity):
    line_item = LineItem(cart.id, product_id, quantity)
    return line_item

ulc = ULContext({
    'product_id': UUID(),
    'line_item': Type(LineItem)
})

__hansel_ul__.ulc[id(ulc)] = ulc


code = ast.parse(get_source(order_item))
transform(code, validation_pipe_transform(ulc))
transform(code, func_validation_transform(ulc))
print(ast.dump(code.body[0].body[1]))
print(astor.to_source(code))

code_obj = compile(code, '<>', 'exec')
exec(code_obj)


