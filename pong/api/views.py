from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext as _
from rest_framework import status

def csrf_failure(request, reason=""):
	return Response({'detail' : _('CSRF token missing')}, status=status.HTTP_403_FORBIDDEN)

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})
	
class CurrentServerTimeView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		return Response({'server_time' : now().isoformat()})
