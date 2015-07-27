import unittest

import nose.tools as nt

from ..service import Service
from earthdragon.typelet import Int, UUID


class ServiceTest(unittest.TestCase):
    def setUp(self):
        pass

class DaleService(Service):
    with Service.UL():
        wheee = Int()

    def bob(self, wheee):
        self.wheee = wheee

def test_service_ul():
    raise NotImplementedError()
    # currently fails assert and does not raise
    with nt.assert_raises(TypeError):
        ds = DaleService()
        ds.bob('string')
