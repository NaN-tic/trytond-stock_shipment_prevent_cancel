# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from collections import defaultdict

from trytond.model import ModelView, Workflow
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction


class ShipmentIn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cancel = cls._buttons['cancel']
        cancel['invisible'] |= Eval('state') == 'received'
        cls._transitions.discard(('received', 'cancelled'))
        cls._transitions.add(('received', 'draft'))
        cls._buttons['draft']['invisible'] = (
            ~Eval('state').in_(['received', 'cancelled']))

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, shipments):
        pool = Pool()
        Move = pool.get('stock.move')
        Product = pool.get('product.product')
        received = [s for s in shipments if s.state == 'received']
        moves = [m for s in received for m in s.incoming_moves
            if m.state == 'done']
        costs = defaultdict(list)
        for move in moves:
            costs[move._cost_price_key()].append(
                (move.product.id, move.effective_date))

        # Check the original dates before resetting any reception data.
        Move.check_period_closed([m for s in received for m in s.moves])
        # Reset only this shipment's incoming moves. Move.draft does not
        # support done moves, and dates cannot be changed while still done.
        Move.write(moves, {'state': 'draft'})
        Move.write(moves, {'effective_date': None})
        super().draft(shipments)
        cls.write(received, {'received_by': None, 'effective_date': None})

        for key, values in costs.items():
            with Transaction().set_context(dict(key)):
                products = Product.browse(list({p for p, _ in values}))
                Product.recompute_cost_price(
                    products, start=min(d for _, d in values))


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
