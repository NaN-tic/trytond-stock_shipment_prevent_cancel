# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['ShipmentIn', 'ShipmentOut']


class ShipmentIn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    def __setup__(cls):
        super(ShipmentIn, cls).__setup__()
        cancel = cls._buttons['cancel']
        cancel['invisible'] |= Eval('state') == 'received'


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        cancel = cls._buttons['cancel']
        cancel['invisible'] |= Eval('state').in_(['assigned', 'packed'])
