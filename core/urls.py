from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us_page'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_page'),
    path('faq/', views.FAQView.as_view(), name='faq_page'),
]
