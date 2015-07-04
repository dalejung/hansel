import unittest
import nose.tools as nt
from ..repo import Repo
from ..finder import RepoFinder, MissingIndexError
from hansel.traits import UUID, Dict

def test_repo_persist():
    # assert False, "TODO: Keep track of Repo instances and persist their data via pickle"
    pass

def test_repo_aggregate_scaffolding():
    #assert False, "TODO: Let Repo define an aggregate, then type check"
    pass

class Obj:
    def __init__(self, id, user_id, product_id):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id

class TestRepoFinder(unittest.TestCase):
    def test_save(self):
        indexer = RepoFinder(None, {'user_id':{}, 'product_id': {}})
        indexer.save(Obj(1, 123, 4))
        indexer.save(Obj(3, 123, 5))
        # only saving objects for one user
        user_id_index = indexer.indexers['user_id']
        nt.assert_count_equal(user_id_index, [123])
        # get obj for user, check ids
        obj_for_user = user_id_index[123]
        nt.assert_count_equal(obj_for_user, [1,3])

        # saved obj for two products
        product_id_index = indexer.indexers['product_id']
        nt.assert_count_equal(product_id_index, [4,5])

        objs_for_product = product_id_index[4]
        nt.assert_count_equal(objs_for_product, [1])

    def test_find_by(self):
        indexer = RepoFinder(None, {'user_id':{}, 'product_id': {}})
        indexer.save(Obj(1, 123, 4))
        indexer.save(Obj(3, 123, 5))

        indexer.by_user_id # yay
        with nt.assert_raises(MissingIndexError):
            indexer.by_bob # nay

        # non by_* attrs follow regular attribute lookup
        with nt.assert_raises(AttributeError):
            indexer.wrong_attr

    def test_find_by_mutate(self):
        """
        Test that all queries are correct after updating objects with
        changed indexed values
        """
        indexer = RepoFinder(None, {'user_id':{}, 'product_id': {}})
        obj = Obj(1, 123, 4)
        indexer.save(obj)
        nt.assert_is(indexer.find('product_id', 4)[1], obj)
        obj.product_id = 8
        indexer.save(obj)
        # update correctly retursn for new product_id
        nt.assert_is(indexer.find('product_id', 8)[1], obj)
        nt.assert_not_in(1, indexer.find('product_id', 8))
