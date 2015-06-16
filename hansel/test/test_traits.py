import unittest

import nose.tools as nt

from ..traits import Int, List, Dict, TraitError, KeyTypeError

class V:
    pass

class ExampleObj:
    dct = Dict(int)
    dct_key = Dict(int, key_class=str)
    lst = List(V)

class Dict(unittest.TestCase):
    def test_validate(self):
        with nt.assert_raises(TraitError):
            ex = ExampleObj()
            ex.dct = []

        ex = ExampleObj()
        ex.dct = {'int1': 123, 3: 123}

        with nt.assert_raises(TraitError):
            ex.dct = {'int1': 123, 'float1': 1.1}

    def test_keyclass(self):
        with nt.assert_raises(KeyTypeError):
            ex = ExampleObj()
            ex.dct_key = {'int1': 123, 3: 123}

class List(unittest.TestCase):
    def test_validate(self):
        with nt.assert_raises(TraitError):
            ex = ExampleObj()
            ex.lst = {}

        ex = ExampleObj()
        ex.lst = [V(), V()]

        with nt.assert_raises(TraitError):
            ex.lst = [V(), V(), 3]
