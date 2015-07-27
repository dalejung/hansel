import nose.tools as nt

from ..entity import Entity, mutate, UnexpectedMutationError

class Test(Entity):
    def __init__(self, hello):
        super().__init__()
        self.hello = hello

    @mutate
    def change_hello(self, hello, frank=1):
        if hello > 0:
            raise Exception('whatever')
        with mutate.apply:
            self.hello = hello
        return 1

t = Test('hi')
t.change_hello(-10)


class Bob(Entity):
    def __init__(self, bob):
        super().__init__()
        self.bob = bob

    @mutate
    def hello(self, bob):
        self.bob = bob

class Frank(Bob):
    def __init__(self, bob):
        super().__init__(bob)
        self.bob = bob

    def bye(self,bye):
        self.bob = bye
        print(bye)

b = Bob(1)
nt.assert_equal(b.bob, 1)
b.hello(10)
nt.assert_equal(b.bob, 10)

f = Frank(100)
with nt.assert_raises(UnexpectedMutationError):
    f.bye(1)

f.hello(10)
nt.assert_equal(f.bob, 10)
