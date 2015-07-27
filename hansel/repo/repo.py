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
from enum import Enum
from functools import partial

from hansel.meta import MetaMeta
from earthdragon.typelet import Dict

from .finder import RepoFinder
from .auto_repo import process

# TODO make a util errors class
class InvalidRepoError(Exception):
    pass

class RepoConf:

    init = False
    aggregate = False

    def __init__(self, dct):
        if '__init__' in dct:
            self.init = True
        aggregate = dct.get('aggregate', False)
        if aggregate and inspect.isclass(aggregate):
            self.aggregate = True

    @property
    def invalid_repo(self):
        return not self.aggregate and not self.init

    @property
    def is_auto_repo(self):
        return self.aggregate and not self.init


class RepoMeta(MetaMeta):
    def setitem_handler(key, value, scope):
        # raise NotImplementedError?
        pass

    def __new__(cls, name, bases, dct):

        if bases: # only run for Repo subclass, not repo itself
            conf = RepoConf(dct)
            if conf.invalid_repo:
                raise InvalidRepoError("Repo subclass requires aggregate"
                                       " if missing init")

            if conf.is_auto_repo:
                process(cls, name, bases, dct)

        return super().__new__(cls, name, bases, dct)

class Repo(metaclass=RepoMeta):
    pass
