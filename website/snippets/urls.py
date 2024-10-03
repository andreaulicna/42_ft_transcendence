from django.urls import path
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
	path('', views.api_root),
	path('snippets-list', views.SnippetList.as_view(), name="snippet-list"),
	path('snippets-list/<int:pk>/', views.SnippetDetail.as_view(), name="snippet-detail"),
	path('snippets-list/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name="snippet-highlight"),
	path('users/', views.UserList.as_view(), name="user-list"),
	path('users/<int:pk>/', views.UserDetail.as_view(), name="user-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)