# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class StockShipmentPreventCancelTestCase(ModuleTestCase):
    'Test Stock Shipment Prevent Cancel module'
    module = 'stock_shipment_prevent_cancel'

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            StockShipmentPreventCancelTestCase))
    return suite
