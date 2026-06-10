from decimal import Decimal
from typing import List, Optional
from ..models.shipping import ShippingRule


class ShippingCalculationResult:
    """Simple data container for a shipping option returned to the storefront."""
    def __init__(self, rule_id: str, title: str, fee: Decimal, estimated_days: str):
        self.rule_id = rule_id
        self.title = title
        self.fee = fee
        self.estimated_days = estimated_days


class ShippingService:
    """
    Stateless service that calculates shipping fees.

    Currently uses the Manual (database-driven) provider.
    Future: detect active courier API providers (Pathao, Aramex) from ShippingProvider
    table and delegate to their respective API clients.
    """

    @staticmethod
    def calculate_fee(
        province: str = '',
        district: str = '',
        city: str = '',
        order_total: Decimal = Decimal('0.00')
    ) -> Optional[ShippingCalculationResult]:
        """
        Main entry point for shipping fee calculation.
        Returns a single ShippingCalculationResult, or None if no rule matches.
        """
        from ..selectors.shipping_selectors import get_rule_for_address

        rule = get_rule_for_address(province=province, district=district, city=city)

        if not rule:
            return None

        return ShippingCalculationResult(
            rule_id=str(rule.id),
            title=rule.title,
            fee=rule.shipping_fee,
            estimated_days=rule.estimated_days
        )

    # ------------------------------------------------------------------
    # Future: Add courier API support here
    # ------------------------------------------------------------------
    # @staticmethod
    # def calculate_fee_via_pathao(province, district, order_total):
    #     provider = ShippingProvider.objects.get(code='pathao', is_active=True)
    #     api_key = provider.configuration.get('api_key')
    #     # ... call Pathao API ...
