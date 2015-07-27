import unittest

import nose.tools as nt

from ..value_object import ValueObject, IllegalMutation, InvalidInitInvocation
from earthdragon.typelet import Int, UUID, Unicode

def test_immutability():
    """
    Test that ValueObject attributes do not get set after construction
    """
    class VO(ValueObject):
        id = Int()

        def __init__(self, id):
            self.id = id

    vo = VO(3)
    with nt.assert_raises(IllegalMutation):
        vo.id = 4
    nt.assert_equals(vo.id, 3)

class Parent(ValueObject):
    id = Int()

    def __init__(self, id):
        self.id = id

class Child(Parent):
    id2 = Int()

    def __init__(self, id, id2):
        self.id2 = id2
        super().__init__(id)

class GrandChild(Child):
    id3 = Int()

    def __init__(self, id, id2, id3):
        self.id3 = id3
        super().__init__(id, id2)



def test_hansle_typelets():
    """
    hansel typelets should be a complete list. this means
    it will contain superclass typelets as well.
    """
    nt.assert_count_equal(Parent._earthdragon_typelets, ['id'])
    nt.assert_count_equal(Child._earthdragon_typelets, ['id', 'id2'])
    nt.assert_count_equal(GrandChild._earthdragon_typelets, ['id', 'id2', 'id3'])

def test_subclass_values():
    gc = GrandChild(100, 200, 300)
    nt.assert_equal(gc.id, 100)
    nt.assert_equal(gc.id2, 200)
    nt.assert_equal(gc.id3, 300)

    child = Child(100, 200)
    nt.assert_equal(child.id, 100)
    nt.assert_equal(child.id2, 200)

def test_init():
    """
    Test that the default inits are very strict
    """
    class DefaultInit(ValueObject):
        id = Int()
        name = Unicode()

    obj = DefaultInit(1, "Dale")
    obj = DefaultInit(name="Dale", id=1)

    with nt.assert_raises(InvalidInitInvocation):
        obj = DefaultInit()

    with nt.assert_raises(InvalidInitInvocation):
        obj = DefaultInit(1, "DALE", extra=123)

    with nt.assert_raises(InvalidInitInvocation):
        obj = DefaultInit(1, "DALE", 123)
