from rest_framework.exceptions import APIException
from rest_framework import status

class InsufficientStockException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Requested quantity exceeds available inventory.'
    default_code = 'INSUFFICIENT_STOCK'

class VariantNotAvailableException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Variant is not available for purchase.'
    default_code = 'VARIANT_NOT_AVAILABLE'

class CartItemNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Cart item not found.'
    default_code = 'CART_ITEM_NOT_FOUND'
