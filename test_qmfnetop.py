import unittest
from pxe import Pxe

import qmfnetop

class TestQmfNetOp(unittest.TestCase):

    def setUp(self) -> None:
        qmfnetop.QMFNetOp.SETTTINGS_FILE = 'test/settings.yml'
        
        return super().setUp()


    def test_read_setting(self):
        net = qmfnetop.QMFNetOp()
        # test data should contain 5 host of Pxe instance.
        pxes = net.pxes
        self.assertEqual(len(pxes), 6)
        for p in pxes:
            self.assertIsInstance(p, Pxe)
        