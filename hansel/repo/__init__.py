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

from .meta import MetaMeta
from .traits import Dict

# TODO make a util errors class
class InvalidRepoError(Exception):
    pass

class MissingIndexError(Exception):
    pass

class InvalidIndexError(Exception):
    _msg_template = "{index_name} does is invalid for aggregate"
    def __init__(self, index_name):
        msg = self._msg_template.format(index_name=index_name)
        super().__init__(msg)

class RepoFinder:
    def __init__(self, aggregate, indexers):
        self.aggregate = aggregate
        self.indexers = indexers
        self.finders = {}

    def save(self, obj):
        for idx_name, indexer in self.indexers.items():
            key = getattr(obj, idx_name)
            current = indexer.setdefault(key, {})
            current[obj.id] = obj

    def _find(self, cond, index_name):
        indexer = self.indexers[index_name]
        return indexer.get(cond, {})

    # cache find partial
    def _finder(self, name):
        if name not in self.finders:
            self.finders[name] = partial(self._find, index_name=name)

        return self.finders[name] 

    def __getattr__(self, name):
        if not name.startswith('by_'):
            return super().__getattr__(name)

        index_name = name[3:]
        if index_name not in self.indexers:
            msg = ("Tried to query by {index_name}"
                " but index does not exist on repo")
            msg = msg.format(index_name=index_name)
            raise MissingIndexError(msg)
        return self._finder(index_name)

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
                AutoRepoProcess.apply(name, bases, dct)

        return super().__new__(cls, name, bases, dct)

class Repo(metaclass=RepoMeta):
    pass

class AutoRepoTemplate:
    # really just a namespace. these methods will live on Repo
    # if it goes through AutoRepoProcess.apply
    def __init__(self):
        self.data = {}
        finder = AutoRepoTemplate._generate_finder(self.aggregate, self.indexes)
        self.finder = finder

    def _generate_finder(aggregate, indexes):
        indexers = {}
        for index_name in indexes:
            indexers[index_name] = {}
        finder = RepoFinder(aggregate, indexers)
        return finder

    def save(self, obj):
        if not isinstance(obj, self.aggregate):
            msg = "Repo can only save {name} aggregates."
            msg = msg.format(name=self.aggregate.__name__)
            raise TypeError(msg)
        self.data[obj.id] = obj
        self.finder.save(obj)

class AutoRepoProcess:
    @classmethod
    def apply(cls, name, bases, dct):
        template = AutoRepoTemplate
        aggregate = dct['aggregate']
        dct['data'] = Dict(aggregate)
        indexes = dct.get('indexes', [])

        for method in ['__init__', '_generate_finder', 'save']:
            if method in dct:
                # raise warning if method already exists
                continue
            dct[method] = getattr(template, method)

        cls.validate_indexes(aggregate, indexes)

    @classmethod
    def validate_indexes(cls, aggregate, indexes):
        for index_name in indexes:
            if not hasattr(aggregate, index_name):
                raise InvalidIndexError(index_name)

if __name__ == '__main__':
    from .traits import UUID
    class SomeAggregate:
        id = UUID()
        user_id = UUID()
        product_id = UUID()

    class TestRepo(Repo):
        aggregate = SomeAggregate
        indexes = ['user_id', 'product_id']

    tr = TestRepo()
