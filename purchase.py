# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, Workflow
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction, without_check_access


class ShipmentIn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in'

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, shipments):
        Purchase = Pool().get('purchase.purchase')
        transaction = Transaction()
        with without_check_access():
            purchases = {m.purchase for s in shipments
                for m in s.incoming_moves if m.purchase}
        super().draft(shipments)
        if purchases:
            with transaction.set_context(
                    queue_batch=transaction.context.get('queue_batch', True)):
                Purchase.__queue__.process(purchases)
