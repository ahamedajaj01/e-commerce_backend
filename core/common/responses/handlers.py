from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def global_exception_handler(exc, context):
    """
    Standardizes error responses across the platform.
    """
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        message = ""
        # Handle dict errors (mostly validation)
        if isinstance(response.data, dict):
            # If it's a detail key, use it
            if 'detail' in response.data:
                message = response.data['detail']
            else:
                # Format validation errors into a string
                message = "; ".join([f"{k}: {v}" for k, v in response.data.items()])
        elif isinstance(response.data, list):
            message = "; ".join([str(v) for v in response.data])
        else:
            message = str(response.data)

        response.data = {
            "success": False,
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": message,
            }
        }
    else:
        # For unhandled exceptions (Server errors)
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return Response({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred on the server."
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
