from hansel.traits import Dict

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

def validate_indexes(aggregate, indexes):
    for index_name in indexes:
        if not hasattr(aggregate, index_name):
            raise InvalidIndexError(index_name)

def generate_find_funcs(dct, indexes):
    raise NotImplementedError()

def process(cls, name, bases, dct):
    template = AutoRepoTemplate
    aggregate = dct['aggregate']
    dct['data'] = Dict(aggregate)
    indexes = dct.get('indexes', [])

    for method in ['__init__', '_generate_finder', 'save']:
        if method in dct:
            # raise warning if method already exists
            continue
        dct[method] = getattr(template, method)

    validate_indexes(aggregate, indexes)
    generate_find_funcs(dct, indexes)

if __name__ == '__main__':
    from .repo import Repo
    from hansel.traits import UUID
    class SomeAggregate:
        id = UUID()
        user_id = UUID()
        product_id = UUID()

    class TestRepo(Repo):
        aggregate = SomeAggregate
        indexes = ['user_id', 'product_id']

    tr = TestRepo()

