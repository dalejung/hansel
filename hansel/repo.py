"""
Target example usage:

class TestRepo(Repo):
    aggregate = Member
    indexes = Member.id, Member.name

When special class variables are set, we do something like flush the class
namespace with special methods/variables. Essentially building out directives
that auto scaffold find_by_name type of methods. Also auto provide the in
memory hashes to support the functionality.
"""
import inspect
import ctypes

def reload_locals(frame):
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(1))


class RepoDict(dict):
    def __setitem__(self, key, value):
        if key == 'something':
            pass
        super().__setitem__(key, value)

class RepoMeta(type):

    @classmethod
    def __prepare__(mcl, name, bases):
        return RepoDict()

class Repo(metaclass=RepoMeta):
    pass
