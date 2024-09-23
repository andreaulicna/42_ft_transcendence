from django.urls import path
from . import views

app_name = 'pong'
urlpatterns = [
	path('toggle-color/', views.toggle_color, name='toggle_color'),
	path('', views.game, name='game'), # ex: /pong
]