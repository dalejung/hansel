import unittest
import nose.tools as nt
from ..repo import Repo, RepoFinder, InvalidIndexError, MissingIndexError, InvalidRepoError
from ..traits import UUID, Dict

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

class SomeAggregate:
    id = UUID()
    user_id = UUID()
    product_id = UUID()

class TestRepo(unittest.TestCase):
    def test_invalid_repo(self):
        """
        Repos that don't have an explicit init, must instead define an
        aggregate to kick off the auto repo wrapping
        """
        with nt.assert_raises(InvalidRepoError):
            class TestRepo(Repo):
                pass

    def test_auto_repo_data(self):
        """ testing the creation of the data trait from aggregate """
        class TestRepo(Repo):
            aggregate = SomeAggregate

        tr = TestRepo()
        data_trait = TestRepo.__dict__['data']
        nt.assert_is_instance(data_trait, Dict)
        nt.assert_is(data_trait.check_class, SomeAggregate)

    def test_auto_indexes(self):
        with nt.assert_raises(InvalidIndexError):
            class IncorrectIndexesTestRepo(Repo):
                aggregate = SomeAggregate
                indexes = ['user_id', 'wrong_index']
