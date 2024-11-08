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
from api.models import WebSocketTicket
from django.core.cache import cache
from api.views import LoginView, RefreshView

from pprint import pprint
def print_websocket_tickets():
    tickets = WebSocketTicket.objects.all().values('user__username', 'uuid', 'created_at', 'expires_at')
    pprint(list(tickets))

# own authentication view that checks the database for the uuid - should be probably moved to views.py
class WsLoginView(APIView):
	"""
		get:
			custom API view for retrieving ticket to connect to websocket.
	"""
	permission_classes = (IsAuthenticated,)

	def get(self, request, *args, **kwargs):
		ticket_uuid = uuid.uuid4()
		user_id = request.user.id
		expires_at = timezone.now() + timedelta(minutes=10)
		cache.set(ticket_uuid, user_id, 600)
		
		WebSocketTicket.objects.create(
			user=request.user,
			uuid=ticket_uuid,
			expires_at=expires_at
		)
		#print_websocket_tickets()
		return Response({'uuid': ticket_uuid})

urlpatterns = [
	path('admin/', admin.site.urls),
	#path('api/auth/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	#path('api/auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/auth/login', LoginView.as_view(),name = "login"),
	path('api/auth/login/refresh', RefreshView.as_view(),name = "login-refresh"),
	path('api/auth/ws-login', AsgiValidateTokenView.as_view())
]

