from functools import partial
from earthdragon.typelet import Dict

from .finder import RepoFinder

class InvalidIndexError(Exception):
    _msg_template = "{index_name} does is invalid for aggregate"
    def __init__(self, index_name):
        msg = self._msg_template.format(index_name=index_name)
        super().__init__(msg)

class AutoRepoTemplate:
    # really just a namespace. these methods will live on Repo
    # if it goes through AutoRepoProcess.apply
    def __init__(self):
        self.data = {}
        finder = AutoRepoTemplate._generate_finder(self.aggregate, self.indexes)
        self.finder = finder

    def get(self, id):
        return self.data.get(id, None)

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

    def get_all(self):
        return self.data

def validate_indexes(aggregate, indexes):
    for index_name in indexes:
        if not hasattr(aggregate, index_name):
            raise InvalidIndexError(index_name)

def generate_find_funcs(aggregate, indexes, dct):
    def _gen_func(index_name, unique):
        def _find(self, cond):
            res = self.finder.find(index_name, cond)
            if not res:
                return None

            if unique:
                res = next(iter(res.values()))
            return res
        return _find

    for index_name in indexes:
        attr = getattr(aggregate, index_name)
        find_func = _gen_func(index_name, unique=attr.unique)
        dct['by_' + index_name] = find_func

def process(cls, name, bases, dct):
    template = AutoRepoTemplate
    aggregate = dct['aggregate']
    dct['data'] = Dict(aggregate)
    indexes = dct.setdefault('indexes', [])

    for method in ['__init__', '_generate_finder', 'save', 'get', 'get_all']:
        if method in dct:
            # raise warning if method already exists
            continue
        dct[method] = getattr(template, method)

    validate_indexes(aggregate, indexes)
    generate_find_funcs(aggregate, indexes, dct)
