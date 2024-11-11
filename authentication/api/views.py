from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.middleware import csrf
from django.utils import timezone
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import CustomTokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
        
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class LoginView(APIView):
    def post(self, request, format=None):
        data = request.data
        response = Response()
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                response.set_cookie(
                                    key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
                                    value = data["refresh"],
                                    expires = expires,
                                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                                    path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
                                        )
                csrf.get_token(request)
                response.data = {"refresh": data['refresh'], "access" : data['access']}
                
                return response
            else:
                return Response({"details" : "This account is not active"},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"details" : "Invalid username or password"},status=status.HTTP_404_NOT_FOUND)

class RefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    def post (self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            response = Response()
            if serializer.is_valid():
                data = serializer.validated_data
                expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                response.set_cookie(
                                    key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                                    value = data["refresh"],
                                    expires = expires,
                                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                                    path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
                                    )
                csrf.get_token(request)
                response.data = data

                return response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"details" : str(e)},status=status.HTTP_401_UNAUTHORIZED)