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
