import unittest
import nose.tools as nt
from ..repo import Repo, InvalidRepoError
from ..finder import RepoFinder, MissingIndexError
from ..auto_repo import InvalidIndexError
from hansel.traits import Dict, Int

def test_repo_persist():
    # assert False, "TODO: Keep track of Repo instances and persist their data via pickle"
    pass

def test_repo_aggregate_scaffolding():
    #assert False, "TODO: Let Repo define an aggregate, then type check"
    pass

class SomeAggregate:
    id = Int()
    user_id = Int()
    product_id = Int()

    def __init__(self, id, user_id, product_id):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id

    def __repr__(self):
        return "SomeAggregate:"+str(repr(self.__dict__))

DATA = {
    1: {
        'id': 1,
        'user_id': 22,
        'product_id': 111
    },
    2: {
        'id': 2,
        'user_id': 22,
        'product_id': 222
    },
    4: {
        'id': 4,
        'user_id': 25,
        'product_id': 222
    },
}

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

    def setUp(self):
        print('setup')

        self.data = DATA

    def check_obj_against_data(self, obj):
        data = self.data
        rec = data[obj.id]
        for k, v in rec.items():
            nt.assert_equal(rec[k], getattr(obj, k))

    @staticmethod
    def gen_repo(data):
        class TestRepo(Repo):
            aggregate = SomeAggregate
            indexes = ['user_id', 'product_id']

        tr = TestRepo()
        # add to repo
        for id, rec in data.items():
            obj = SomeAggregate(**rec)
            tr.save(obj)
        return tr

    def test_auto_finder(self):

        data = self.data
        tr = self.gen_repo(data)

        # test get
        for id in data:
            obj = tr.get(id)
            self.check_obj_against_data(obj)

        # check by user
        user_res = tr.by_user_id(22)
        for id, obj in user_res.items():
            self.check_obj_against_data(obj)

        nt.assert_count_equal(user_res, [1, 2])

        user_res = tr.by_user_id(25)
        nt.assert_count_equal(user_res, [4])


    def test_update_obj(self):
        """ """
        data = self.data
        tr = TestRepo.gen_repo(data)

        # change obj
        obj = tr.get(4)
        obj.user_id = 99
        tr.save(obj)

        # obj with id == 4 changed user_id 25 -> 99
        # obj should not be returned for user_id
        # 07-03-15 currently broken
        old_user_objs = tr.by_user_id(25)
        nt.assert_not_in(4, old_user_objs)
