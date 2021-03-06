import nose.tools as nt

from ..entity import Entity, mutate, UnexpectedMutationError
from earthdragon.typelet import Int

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


def test_split_apply():
    class SplitApply(Entity):
        var = Int()

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

    new_obj = SplitApply.load_from_history(obj._events)
    nt.assert_equal(new_obj.var, obj.var)

def test_default_init():
    class DefaultEntity(Entity):
        id = Int(required=True)
        age = Int()
        def_num = Int(default=100)

        @mutate
        def change_age(self, age):
            self.age = age

    de = DefaultEntity(10)
    nt.assert_equal(de.id, 10)
    nt.assert_equal(de.def_num, 100)

    with nt.assert_raises(UnexpectedMutationError):
        de.age = 10

    de.change_age(98)
    nt.assert_equal(de.age, 98)
