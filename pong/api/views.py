from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})
	
class CurrentServerTimeView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		return Response({'server_time' : now().isoformat()})
