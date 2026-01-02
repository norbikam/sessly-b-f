from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListApiView
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Favorite
from businesses.models import Business
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    ResendVerificationEmailSerializer,
    UserSerializer,
    VerifyEmailSerializer,
    FavoriteSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        print('📥 Registration request data:', request.data)
        
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            print('❌ VALIDATION ERRORS:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Stwórz użytkownika
        user = serializer.save()
        print(f'✅ User created: {user.username}')
        
        # Wygeneruj tokeny JWT
        refresh = RefreshToken.for_user(user)
        
        # Zwróć dane użytkownika + tokeny
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active:
            if getattr(settings, "EMAIL_VERIFICATION_ENABLED", True):
                raise AuthenticationFailed("Potwierdz adres email zanim sie zalogujesz.")

            self.user.is_active = True
            self.user.save(update_fields=["is_active"])
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Adres email zostal potwierdzony"}, status=status.HTTP_200_OK)


class ResendVerificationCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Nowy kod zostal wyslany"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Haslo zostalo zmienione"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Brak tokenu refresh"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Nie udalo sie uniewaznic tokenu"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_205_RESET_CONTENT)
    
class ToggleFavoriteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, business_id):
        business = get_object_or_404(Business, id=business_id)

        favorite_query = Favorite.objects.filter(user=request.user, business=business)

        if favorite_query.exists():
            favorite_query.delete()
            return Response(
                {"detail": "Usunięto z ulubionych", "is_favorite": False}
            )
        else:
            Favorite.objects.create(user=request.user, business=business)
            return Response(
                {"details": "Dodano do ulubionych", "is_favorite": True},
                status=status.HTTP_201_CREATED
            )
        
class UserFavoritesView(ListApiView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('business')
