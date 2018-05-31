# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
# import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_depends


class TestCase(unittest.TestCase):
    'Test module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('stock_shipment_prevent_cancel')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    return suite
