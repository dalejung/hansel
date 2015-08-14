import nose.tools as nt

from ..entity import Entity, mutate, UnexpectedMutationError

def test_simple_event_source():
    class PositiveNumber(Entity):
        def __init__(self, num):
            self.num = num
            super().__init__()

        @mutate
        def change_num(self, num, other=1):
            if num < 0:
                raise Exception('Can only be positive')
            self.num = num

    t = PositiveNumber(1)
    with nt.assert_raises(UnexpectedMutationError):
        t.num = 10
    t.change_num(10)
    nt.assert_equal(t.num, 10)
    init_event = t._events[0]
    nt.assert_dict_equal(init_event.__dict__, {'num': 1})
    change_num_event = t._events[1]
    nt.assert_dict_equal(change_num_event.__dict__, {'num': 10, 'other': 1})


class SplitApply(Entity):
    def __init__(self, var):
        with mutate.apply:
            self.var = var

    @mutate
    def change_var(self, var):
        with mutate.apply:
            self.var = var

obj = SplitApply(1)
for ev in obj._events:
    obj.apply(ev)
nt.assert_equal(obj.var, 1)

obj.change_var(10)
for ev in obj._events[1:]:
    obj.apply(ev)

nt.assert_equal(obj.var, 10)
