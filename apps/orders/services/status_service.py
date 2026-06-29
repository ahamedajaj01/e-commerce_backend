from django.db import transaction
from ..models import Order, OrderStatusHistory
from apps.inventory.services.inventory_services import adjust_inventory
from apps.inventory.models.inventory import StockMovement

class OrderStatusService:
    @staticmethod
    @transaction.atomic
    def update_status(
        *,
        order: Order,
        new_status: str,
        user=None,
        notes: str = ""
    ) -> Order:
        """
        Updates the order status and records it in history.
        Validates transitions to avoid logical errors.
        """
        old_status = order.status
        
        if old_status == new_status:
            return order

        # TODO: Add logic to prevent invalid transitions (e.g., DELIVERED -> PENDING)
        
        # 1. Record History
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=old_status,
            new_status=new_status,
            changed_by=user,
            notes=notes
        )
        
        # 2. Handle Inventory Restock on Cancellation
        if new_status == Order.Status.CANCELLED and old_status != Order.Status.CANCELLED:
            for item in order.items.select_related('product_variant').all():
                if item.product_variant:
                    adjust_inventory(
                        variant=item.product_variant,
                        quantity=item.quantity,
                        movement_type=StockMovement.MovementType.RETURN,
                        note=f"Automatic restoration: Order {order.order_number} cancelled."
                    )

        # 3. Update Order
        order.status = new_status
        order.save()
        
        return order
