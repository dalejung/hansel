from ..value_object import ValueObject, IllegalMutation
from ..traits import Int

import nose.tools as nt

class VO(ValueObject):
    id = Int(immutable=True)

    def __init__(self, id):
        self.id = id

vo = VO(3)
with nt.assert_raises(IllegalMutation):
    vo.id = 4

with nt.assert_raises(Exception):
    class NoInit(ValueObject):
        pass
