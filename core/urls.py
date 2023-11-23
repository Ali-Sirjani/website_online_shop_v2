from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
