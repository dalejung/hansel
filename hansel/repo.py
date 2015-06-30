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
from .meta import MetaMeta

class RepoMeta(MetaMeta):
    pass

class Repo(metaclass=RepoMeta):
    pass
