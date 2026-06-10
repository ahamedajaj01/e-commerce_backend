from typing import Any, Optional
from rest_framework.response import Response
from rest_framework import status

def success_response(data: Any = None, message: str = "Operation successful", status_code: int = status.HTTP_200_OK) -> Response:
    """Standard success response format."""
    return Response({
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }, status=status_code)

def error_response(message: str, code: str = "ERROR", data: Any = None, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """Standard error response format."""
    return Response({
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "data": data if data is not None else {}
        }
    }, status=status_code)
