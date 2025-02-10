"""
URL configuration for pong project.

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
from django.urls import path
from api.views import HealthCheckView, CurrentServerTimeView, MatchesInProgressView

urlpatterns = [
    path('admin/', admin.site.urls),
	path('healthcheck', HealthCheckView.as_view()),
	path('api/pong/server-time', CurrentServerTimeView.as_view()),
	path('api/pong/matches-ip', MatchesInProgressView.as_view())
]
