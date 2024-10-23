"""
URL configuration for user_management project.

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
from django.conf import settings
from api import views
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/user/admin', admin.site.urls),
	path('api/user/register', views.UserRegistrationView.as_view(), name='user-registration'),
    path('api/user/login', views.UserLoginView.as_view(), name='user-login'),
	path('api/user/logout', views.UserLogoutView.as_view(), name = 'user-logout'),
	path('api/user/info', views.UserInfoView.as_view(), name='user-info'),
	path('api/user/avatar', views.UserAvatarUpload.as_view(), name='user-avatar-upload'),
	path('api/user/match', views.MatchView.as_view(), name='match-creation'),
	path('api/user/users-list', views.UserListView.as_view(), name='user-list'),
	path('api/user/friendships', views.FriendshipView.as_view(), name='filtered-friendship-list'),
	path('api/user/friendships/<int:pk>', views.FriendshipDeleteView.as_view(), name='friendship-delete'),
	# path('api/user/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/user/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]  
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
