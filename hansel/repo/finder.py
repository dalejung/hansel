from functools import partial

class MissingIndexError(Exception):
    pass

_missing = object()

class RepoFinder:
    def __init__(self, aggregate, indexers):
        self.aggregate = aggregate
        self.indexers = indexers
        self.find_funcs = {}
        self.rev_map = {} # keep track of indexes each obj belongs to

    def remove_from_index(self, index_name, old_val, id):
        current = self.indexers[index_name]
        objects = current[old_val]
        objects.pop(id)

    def save(self, obj):
        print(obj)
        rev_item = self.rev_map.setdefault(obj.id, {})

        for index_name, indexer in self.indexers.items():
            key = getattr(obj, index_name)
            current = indexer.setdefault(key, {})
            current[obj.id] = obj

            old_val = rev_item.get(index_name, _missing)
            if old_val is not _missing and old_val != key:
                self.remove_from_index(index_name, old_val, obj.id)

            rev_item[index_name] = key

    def find(self, index_name, cond):
        indexer = self.indexers[index_name]
        return indexer.get(cond, {})

    # cache find partial
    def _finder(self, name):
        if name not in self.find_funcs:
            self.find_funcs[name] = partial(self.find, index_name=name)

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
