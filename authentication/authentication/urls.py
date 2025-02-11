"""
URL configuration for authentication project.

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_channels_jwt.views import AsgiValidateTokenView
import uuid
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache
from api.views import LoginView, RefreshView, LogoutView, HealthCheckView, IntraAuthorizationView, IntraCallbackView

urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/auth/login', LoginView.as_view(),name = "login"),
	path('api/auth/login/refresh', RefreshView.as_view(),name = "login-refresh"),
	path('api/auth/ws-login', AsgiValidateTokenView.as_view(), name = "websocket-login"),
	path('api/auth/login/refresh/logout', LogoutView.as_view(), name = "logout"),
	path('api/auth/intra', IntraAuthorizationView.as_view(), name = "intra-authorization"),
	path('api/auth/intra/callback', IntraCallbackView.as_view(), name = "intra-callback"),
	path('healthcheck', HealthCheckView.as_view())
]

