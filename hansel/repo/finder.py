from functools import partial

class MissingIndexError(Exception):
    pass

class RepoFinder:
    def __init__(self, aggregate, indexers):
        self.aggregate = aggregate
        self.indexers = indexers
        self.find_funcs = {}

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
        if name not in self.find_funcs:
            self.find_funcs[name] = partial(self._find, index_name=name)

        return self.find_funcs[name] 

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
