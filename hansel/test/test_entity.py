from ..entity import Entity, mutate

class Test(Entity):
    def __init__(self, hello):
        self.hello = hello

    @mutate
    def change_hello(self, hello, frank=1):
        if hello > 0:
            raise Exception('whatever')
        with mutate.apply:
            self.hello = hello
        print('hi', __evt)
        return 1

import ast
import astor
import copy

t = Test('hi')
t.change_hello(-10)
