import uuid
import inspect
import astor
import ast
import types
from asttools import quick_parse, get_source, transform, coroutine

import nose.tools as nt

from ..ul import (
    ULContext,
    validation_pipe_transform,
    func_validation_transform,
    UL,
    wrap_function,
    ul_validate
)
from hansel.traits import UUID, Int, Type, List, TraitError

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

ulc = ULContext({
    'product_id': UUID(),
    'line_item': Type(LineItem)
})


def test_params():
    @ul_validate(ulc)
    def order_item(cart, product_id, quantity):
        line_item = LineItem(cart.id, product_id, quantity)
        return line_item

    with nt.assert_raises(TraitError):
        order_item(Cart(1), 1, 2)
    order_item(Cart(1), uuid.uuid4(), 2)

def test_assignments():
    # try using line_item without it being a LineItem class
    @ul_validate(ulc)
    def order_item(cart, product_id, quantity):
        line_item = [cart.id, product_id, quantity]
        return line_item

    with nt.assert_raises(TraitError):
        order_item(Cart(1), uuid.uuid4(), 2)

    @ul_validate(ulc)
    def order_item(cart, product_id, quantity):
        lst = [cart.id, product_id, quantity]
        return lst

    # fine if we change var name
    order_item(Cart(1), uuid.uuid4(), 2)
