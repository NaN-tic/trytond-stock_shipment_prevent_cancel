# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

from . import purchase, shipment

def register():
    Pool.register(
        shipment.ShipmentIn,
        shipment.ShipmentOut,
        module='stock_shipment_prevent_cancel', type_='model')
    Pool.register(
        purchase.ShipmentIn,
        module='stock_shipment_prevent_cancel', type_='model',
        depends=['purchase'])
