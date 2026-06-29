import uuid
from django.utils import timezone

class OrderNumberService:
    @staticmethod
    def generate() -> str:
        """
        Generates a human-friendly order number.
        Format: ORD-YYYYMMDD-XXXX
        Where XXXX is a short unique suffix.
        """
        now = timezone.now()
        date_str = now.strftime('%Y%m%d')
        unique_suffix = str(uuid.uuid4())[:6].upper()
        return f"ORD-{date_str}-{unique_suffix}"
