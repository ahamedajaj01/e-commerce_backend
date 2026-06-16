from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer
from ..services.auth_service import AuthService
from ..strategies.email_password import EmailPasswordStrategy

from core.common.responses.formatters import success_response, error_response
from apps.users.serializers import UserSerializer
from apps.cart.services.cart_service import merge_guest_cart_into_user_cart, GUEST_TOKEN_COOKIE


def get_auth_service():
    strategy = EmailPasswordStrategy()
    return AuthService(strategy)


class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            service = get_auth_service()
            user = service.authenticate(serializer.validated_data)

            if user:
                refresh = RefreshToken.for_user(user)
                data = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
                response = success_response(data=data, message="Login successful")

                # --- Guest Cart Merge ---
                guest_token = request.COOKIES.get(GUEST_TOKEN_COOKIE)
                if guest_token:
                    try:
                        merge_guest_cart_into_user_cart(user=user, guest_token=guest_token)
                    except Exception:
                        pass  # Never block login due to cart merge failure

                    # Clear the guest cookie since it's been merged
                    response.delete_cookie(GUEST_TOKEN_COOKIE)

                return response

            # If authentication fails, find out why to be more helpful
            from apps.users.models import User
            email = serializer.validated_data.get('email')
            user_exists = User.objects.filter(email=email).exists()
            
            if not user_exists:
                return error_response(
                    message="No account found with this email. Please sign up.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            return error_response(
                message="Invalid password or unverified email.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        return error_response(message="Validation failed", data=serializer.errors)


class MeView(APIView):
    """Returns the profile of the currently authenticated user."""
    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)
