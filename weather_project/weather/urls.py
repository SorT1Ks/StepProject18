from django.urls import path
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.main_view, name='main'),
    path('history/', views.history_view, name='history'),
]
