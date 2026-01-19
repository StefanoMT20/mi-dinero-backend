from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserSettings
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, UserSettingsSerializer


class LoginView(TokenObtainPairView):
    """Vista de login que retorna tokens y datos del usuario."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Vista para cerrar sesión e invalidar el refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {'message': 'Sesión cerrada exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    """Vista para obtener el usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserSettingsView(APIView):
    """Vista para obtener y actualizar la configuración del usuario."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings, created = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={'exchange_rate': 3.75}
        )
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings, created = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={'exchange_rate': 3.75}
        )
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
