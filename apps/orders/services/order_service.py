from django.db import transaction
from ..models import Order, OrderItem
from .order_number_service import OrderNumberService
from .status_service import OrderStatusService
from apps.inventory.services.inventory_services import adjust_inventory
from apps.inventory.models.inventory import StockMovement

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_from_checkout_session(checkout_session) -> Order:
        """
        Main entry point for order creation.
        Builds a permanent Order from a finalized CheckoutSession.
        """
        # 1. Generate unique human-friendly ID
        order_number = OrderNumberService.generate()
        
        # 2. Create the Order (Strict Snapshots)
        order = Order.objects.create(
            order_number=order_number,
            user=checkout_session.user,
            status=Order.Status.PENDING,
            
            # Snapshots from Session
            customer_name=checkout_session.customer_name,
            customer_email=checkout_session.customer_email,
            customer_phone=checkout_session.customer_phone,
            
            shipping_province=checkout_session.shipping_province,
            shipping_district=checkout_session.shipping_district,
            shipping_city=checkout_session.shipping_city,
            shipping_street=checkout_session.shipping_street,
            shipping_instructions=checkout_session.shipping_instructions,
            
            transit_days_min=checkout_session.transit_days_min,
            transit_days_max=checkout_session.transit_days_max,
            processing_days_max=checkout_session.processing_days_max,
            
            subtotal=checkout_session.subtotal,
            shipping_fee=checkout_session.shipping_fee,
            total_price=checkout_session.total_price,
            
            payment_method=checkout_session.payment_method,
            # If online and transaction exists, mark as paid
            is_paid=checkout_session.payment_id != "",
            payment_status=Order.PaymentStatus.PAID if checkout_session.payment_id != "" else Order.PaymentStatus.UNPAID,
            transaction_reference=checkout_session.payment_id
        )
        
        # 3. Create Order Items (Strict Snapshots) & Deduct Inventory
        for cart_item in checkout_session.cart.items.all():
            variant = cart_item.variant
            
            # 🛑 REAL-TIME STOCK CHECK
            if not variant:
                continue

            if variant.stock_quantity < cart_item.quantity:
                raise ValueError(f"Insufficient stock for {variant.product.name} ({variant.sku}). Available: {variant.stock_quantity}")

            # Resolve which image user selected (priority: user selection > variant default)
            selected = cart_item.selected_media
            fallback = variant.image
            image_obj = selected or fallback
            variant_image_url = image_obj.file.url if (image_obj and image_obj.file) else ""

            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                product_id=variant.product_id,
                variant_id=variant.id,
                product_name=variant.product.name,
                variant_name=variant.name,
                sku=variant.sku,
                variant_image=variant_image_url,
                price=variant.price,
                quantity=cart_item.quantity
            )
            
            # 📉 DECREASE STOCK
            adjust_inventory(
                variant=variant,
                quantity=cart_item.quantity,
                movement_type=StockMovement.MovementType.OUT,
                note=f"Automatic deduction for order {order_number}"
            )
            
        # 4. Initialize History
        OrderStatusService.update_status(
            order=order, 
            new_status=Order.Status.PENDING, 
            notes="Order initialized from checkout completion."
        )
        
        return order
