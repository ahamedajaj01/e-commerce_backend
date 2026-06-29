from django.db import models
from django.db.models import Sum, Count
from django.utils import timezone
from apps.orders.models import Order

class AnalyticsSelector:
    @staticmethod
    def get_summary_stats():
        """Calculates high-level business health metrics."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Financial Metrics
        # Only count PAID orders for revenue
        total_revenue = Order.objects.filter(
            payment_status=Order.PaymentStatus.PAID
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Order Status Metrics
        order_counts = Order.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=models.Q(status=Order.Status.PENDING)),
            shipped=Count('id', filter=models.Q(status=Order.Status.SHIPPED)),
            processing=Count('id', filter=models.Q(status=Order.Status.PROCESSING))
        )
        
        # Growth Metrics
        today_orders_count = Order.objects.filter(created_at__gte=today_start).count()
        
        # Add Recent Transactions for Dashboard Table (per UI requirements)
        recent_orders = Order.objects.order_by('-created_at')[:10]
        recent_data = []
        
        progress_map = {
            Order.Status.PENDING: 20,
            Order.Status.CONFIRMED: 40,
            Order.Status.PROCESSING: 60,
            Order.Status.SHIPPED: 80,
            Order.Status.DELIVERED: 100,
            Order.Status.CANCELLED: 0
        }

        for order in recent_orders:
            recent_data.append({
                "transaction_id": order.order_number,
                "customer_identity": order.customer_name or "Guest User",
                "items": order.items.count(),
                "verification": order.payment_status,
                "lifecycle": order.status,
                "progress": progress_map.get(order.status, 0),
                "settlement": float(order.total_price),
                "created_at": order.created_at
            })
        
        return {
            "total_revenue": float(total_revenue),
            "total_orders": order_counts['total'],
            "pending_orders": order_counts['pending'],
            "shipped_orders": order_counts['shipped'],
            "processing_orders": order_counts['processing'],
            "today_orders": today_orders_count,
            "recent_transactions": recent_data,
            "currency": "NPR" 
        }
