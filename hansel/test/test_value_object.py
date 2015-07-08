import unittest

import nose.tools as nt

from ..value_object import ValueObject, IllegalMutation
from ..traits import Int

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



def test_hansle_traits():
    """
    hansel traits should be a complete list. this means
    it will contain superclass traits as well.
    """
    nt.assert_count_equal(Parent._hansel_traits, ['id'])
    nt.assert_count_equal(Child._hansel_traits, ['id', 'id2'])
    nt.assert_count_equal(GrandChild._hansel_traits, ['id', 'id2', 'id3'])

def test_subclass_values():
    gc = GrandChild(100, 200, 300)
    nt.assert_equal(gc.id, 100)
    nt.assert_equal(gc.id2, 200)
    nt.assert_equal(gc.id3, 300)

    child = Child(100, 200)
    nt.assert_equal(child.id, 100)
    nt.assert_equal(child.id2, 200)
