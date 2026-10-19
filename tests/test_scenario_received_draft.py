import unittest
from datetime import date, timedelta
from decimal import Decimal

from proteus import Model
from trytond.model.exceptions import AccessError
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class TestReceivedDraft(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        config = activate_modules('stock_shipment_prevent_cancel')
        create_company()
        company = get_company()
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()
        Uom = Model.get('product.uom')
        unit, = Uom.find([('name', '=', 'Unit')])
        Template = Model.get('product.template')
        template = Template(name='Product', type='goods', default_uom=unit,
            cost_price_method='average')
        template.save()
        product, = template.products
        Product = Model.get('product.product')
        Location = Model.get('stock.location')
        warehouse, = Location.find([('code', '=', 'WH')])
        Shipment = Model.get('stock.shipment.in')
        Move = Model.get('stock.move')
        Period = Model.get('stock.period')
        today = date.today()

        shipments = []
        for days, price in [(5, '2'), (3, '6')]:
            shipment = Shipment(supplier=supplier, warehouse=warehouse,
                planned_date=today - timedelta(days=days),
                effective_date=today - timedelta(days=days))
            shipment.incoming_moves.new(product=product, unit=unit,
                quantity=10, from_location=supplier.supplier_location,
                to_location=warehouse.input_location, company=company,
                unit_price=Decimal(price), currency=company.currency)
            shipment.click('receive')
            self.assertEqual(shipment.state, 'received')
            shipments.append(shipment)

        first, shipment = shipments
        self.assertEqual(Product(product.id).cost_price, Decimal('4'))
        incoming, = shipment.incoming_moves
        inventory_ids = [m.id for m in shipment.inventory_moves]
        shipment.click('cancel')
        self.assertEqual(shipment.state, 'received')
        shipment.click('draft')
        self.assertEqual(shipment.state, 'draft')
        self.assertIsNone(shipment.received_by)
        self.assertIsNone(shipment.effective_date)
        self.assertFalse(shipment.inventory_moves)
        self.assertFalse(Move.find([('id', 'in', inventory_ids)]))
        incoming.reload()
        self.assertEqual(incoming.state, 'draft')
        self.assertIsNone(incoming.effective_date)
        self.assertEqual(Product(product.id).cost_price, Decimal('2'))
        with config.set_context(locations=[warehouse.input_location.id]):
            self.assertEqual(Product(product.id).quantity, 10)

        shipment.incoming_moves[0].unit_price = Decimal('4')
        shipment.effective_date = today - timedelta(days=3)
        shipment.click('receive')
        self.assertEqual(shipment.state, 'received')
        self.assertEqual(len(shipment.inventory_moves), 1)
        self.assertEqual(shipment.incoming_moves[0].id, incoming.id)
        self.assertEqual(Product(product.id).cost_price, Decimal('3'))
        with config.set_context(locations=[warehouse.input_location.id]):
            self.assertEqual(Product(product.id).quantity, 20)

        # Draft moves do not prevent closing a stock period.
        shipment.click('draft')
        period = Period(date=today - timedelta(days=2), company=company)
        period.click('close')
        self.assertEqual(period.state, 'closed')
        # A receipt already included in the closed period cannot be reset.
        with self.assertRaises(AccessError):
            first.click('draft')
        first.reload()
        self.assertEqual(first.state, 'received')
        self.assertEqual(first.incoming_moves[0].state, 'done')
        self.assertEqual(len(first.inventory_moves), 1)

        period.click('draft')
        shipment.effective_date = today
        shipment.click('receive')
        shipment.click('do')
        shipment.click('draft')
        self.assertEqual(shipment.state, 'done')
