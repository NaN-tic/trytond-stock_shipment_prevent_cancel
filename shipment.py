# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval


class ShipmentIn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cancel = cls._buttons['cancel']
        cancel['invisible'] |= Eval('state') == 'received'
        cls._transitions.discard(('received', 'cancelled'))


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cancel = cls._buttons['cancel']
        cancel['invisible'] |= Eval('state').in_(['assigned', 'picked',
                'packed'])
        cls._transitions.discard(('picked', 'cancelled'))
        cls._transitions.discard(('packed', 'cancelled'))
        cls._transitions.discard(('assigned', 'cancelled'))
