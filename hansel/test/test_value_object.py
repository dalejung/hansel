import unittest

import nose.tools as nt

from ..value_object import ValueObject, IllegalMutation, MissingInit
from ..traits import Int

def test_immutability():
    """
    Test that ValueObject attributes do not get set after construction
    """
    class VO(ValueObject):
        id = Int(immutable=True)

        def __init__(self, id):
            self.id = id

    vo = VO(3)
    with nt.assert_raises(IllegalMutation):
        vo.id = 4
    nt.assert_equals(vo.id, 3)

def test_missing_init():
    with nt.assert_raises(MissingInit):
        class NoInit(ValueObject):
            pass
