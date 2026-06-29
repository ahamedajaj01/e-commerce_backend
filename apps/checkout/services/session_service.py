from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from ..models.session import CheckoutSession
from .pricing_service import PricingService
from apps.cart.models.cart import Cart
from apps.shipping.models.shipping import ShippingRule
from apps.catalog.models.product import Product
from apps.orders.services.order_service import OrderService


class CheckoutSessionService:
    @staticmethod
    @transaction.atomic
    def init_session(
        *,
        cart: Cart,
        customer_data: dict,
        shipping_address: dict,
        shipping_rule: ShippingRule,
        payment_method: str = "",
        user=None,
        guest_token=None
    ) -> CheckoutSession:
        """
        Creates a new CheckoutSession by snapshotting current prices, 
        shipping fees, and calculating total delivery ETA.
        """
        # Safeguard: Never store guest token if user is identified
        if user:
            guest_token = None
        # 1. Fetch products to calculate max processing time
        product_ids = [item.variant.product_id for item in cart.items.all()]
        products = Product.objects.filter(id__in=product_ids)
        
        max_proc_min = 0
        max_proc_max = 0
        for p in products:
            max_proc_min = max(max_proc_min, getattr(p, 'processing_days_min', 0))
            max_proc_max = max(max_proc_max, getattr(p, 'processing_days_max', 0))

        # 2. Calculate Pricing
        subtotal = PricingService.calculate_subtotal(cart)
        shipping_fee = shipping_rule.shipping_fee
        total_price = PricingService.calculate_total(subtotal, shipping_fee)

        # 3. Create Session with snapshotted values
        session = CheckoutSession.objects.create(
            cart=cart,
            user=user,
            guest_token=guest_token,
            status=CheckoutSession.Status.DRAFT,
            expires_at=timezone.now() + timedelta(hours=24),
            
            # Customer Data
            customer_name=customer_data['name'],
            customer_email=customer_data['email'],
            customer_phone=customer_data['phone'],
            
            # Address Data
            shipping_province=shipping_address['province'],
            shipping_district=shipping_address['district'],
            shipping_city=shipping_address['city'],
            shipping_street=shipping_address['street'],
            shipping_instructions=shipping_address.get('instructions', ''),
            
            # Shipping Data
            shipping_rule=shipping_rule,
            shipping_rule_title=shipping_rule.title,
            shipping_fee=shipping_fee,
            
            # ETA Data
            transit_days_min=shipping_rule.transit_days_min,
            transit_days_max=shipping_rule.transit_days_max,
            processing_days_max=max_proc_max,
            
            # Pricing Data
            subtotal=subtotal,
            total_price=total_price,
            
            # Payment
            payment_method=payment_method
        )
        return session

    @staticmethod
    @transaction.atomic
    def complete_session(session: CheckoutSession) -> 'Order':
        """
        Converts a valid CheckoutSession into a real Order.
        Delegates the heavy lifting to OrderService.
        """
        if session.status == CheckoutSession.Status.COMPLETED:
            return session.order

        # 1. Promote session to order
        order = OrderService.create_from_checkout_session(session)

        # 2. Finalize Session
        session.status = CheckoutSession.Status.COMPLETED
        session.order = order
        session.save()

        # 3. Cleanup: Deactivate the Cart
        session.cart.status = 'CHECKED_OUT'
        session.cart.save()

        return order
