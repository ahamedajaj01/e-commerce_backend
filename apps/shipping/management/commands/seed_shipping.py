from django.core.management.base import BaseCommand
from apps.shipping.models.shipping import ShippingProvider, ShippingRule


class Command(BaseCommand):
    help = 'Initialize default shipping rules (hierarchical, Google-Places-compatible)'

    def handle(self, *args, **options):
        # 1. Ensure Manual Provider exists (for future courier API pattern)
        ShippingProvider.objects.get_or_create(
            code='manual',
            defaults={
                'name': 'Manual / Internal',
                'provider_type': ShippingProvider.ProviderType.MANUAL,
                'is_active': True
            }
        )

        # 2. Create example hierarchical rules
        rules = [
            {
                'title': 'Kathmandu Metropolitan (Priority 1)',
                'province': 'Bagmati',
                'district': 'Kathmandu',
                'city_or_municipality': 'Kathmandu',
                'shipping_fee': 100.00,
                'estimated_days': '1-2 Business Days',
                'is_default': False,
                'is_active': True,
            },
            {
                'title': 'Kathmandu District (Priority 2)',
                'province': 'Bagmati',
                'district': 'Kathmandu',
                'city_or_municipality': '',
                'shipping_fee': 150.00,
                'estimated_days': '2-3 Business Days',
                'is_default': False,
                'is_active': True,
            },
            {
                'title': 'Bagmati Province (Priority 3)',
                'province': 'Bagmati',
                'district': '',
                'city_or_municipality': '',
                'shipping_fee': 200.00,
                'estimated_days': '3-5 Business Days',
                'is_default': False,
                'is_active': True,
            },
            {
                'title': 'Default Nationwide',
                'province': '',
                'district': '',
                'city_or_municipality': '',
                'shipping_fee': 300.00,
                'estimated_days': '7-10 Business Days',
                'is_default': True,
                'is_active': True,
            },
        ]

        for rule_data in rules:
            obj, created = ShippingRule.objects.get_or_create(
                title=rule_data['title'],
                defaults=rule_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: {obj.title}")

        self.stdout.write(self.style.SUCCESS('\n✅ Shipping rules initialized successfully.'))
