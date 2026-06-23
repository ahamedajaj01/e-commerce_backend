from decimal import Decimal
from typing import Optional
from ..models.shipping import ShippingRule


class ShippingCalculationResult:
    """
    Data container for a shipping option returned to the storefront.
    Focuses exclusively on shipping-related fee and transit time.
    """
    def __init__(
        self, 
        rule_id: str, 
        title: str, 
        fee: Decimal, 
        estimated_days: str,
        transit_days_min: int = 0,
        transit_days_max: int = 0
    ):
        self.rule_id = rule_id
        self.title = title
        self.fee = fee
        self.estimated_days = estimated_days
        self.transit_days_min = transit_days_min
        self.transit_days_max = transit_days_max


class ShippingService:
    """
    Stateless service that calculates shipping fees and identifies transit time.
    
    This service is strictly responsible for shipping domain concerns:
    - Location matching
    - Fee calculation
    - Transit time retrieval (courier journey)
    
    It has no awareness of product processing times or cart contents.
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

        # Return granular transit data alongside legacy string
        return ShippingCalculationResult(
            rule_id=str(rule.id),
            title=rule.title,
            fee=rule.shipping_fee,
            estimated_days=rule.estimated_days,
            transit_days_min=rule.transit_days_min,
            transit_days_max=rule.transit_days_max
        )

    # ------------------------------------------------------------------
    # Future: Add courier API support here
    # ------------------------------------------------------------------
    # @staticmethod
    # def calculate_fee_via_pathao(province, district, order_total):
    #     provider = ShippingProvider.objects.get(code='pathao', is_active=True)
    #     api_key = provider.configuration.get('api_key')
    #     # ... call Pathao API ...
