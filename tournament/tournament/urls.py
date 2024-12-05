"""
URL configuration for tournament project.

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
from django.urls import path, register_converter
from django.conf import settings
from api import views
from django.conf.urls.static import static
from .converters import CapacityConverter

register_converter(CapacityConverter, 'cap')

urlpatterns = [
	path('api/tournament/create/<cap:capacity>/', views.CreateTournamentView.as_view(), name='create-tournament'),
	path('api/tournament/join/<int:tournament_id>/', views.JoinTournamentView.as_view(), name='join-tournament'),
	path('api/tournament/join/cancel/<int:tournament_id>/', views.CancelJoinTournamentView.as_view(), name='cancel-join-tournament'),
	path('api/tournament/list/waiting', views.WaitingTournamentsListView.as_view(), name='list-waiting-tournaments'),
	path('api/tournament/list/player', views.TournamentsListOfPlayerView.as_view(), name='list-tournaments-of-player'),
	path('api/tournament/debug/playertournament/all', views.PlayerTournamentListView.as_view(), name='debug-list-playertournaments'),
	path('api/tournament/debug/tournament/all', views.AllTournamentsListView.as_view(), name='debug-list-tournaments'),
]  
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
