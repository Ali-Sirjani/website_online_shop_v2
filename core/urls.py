from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/set-username/', views.set_username_view, name='set_username'),
    path('profile/address/create', views.CreatProfileAddressView.as_view(), name='profile_create_address'),
    path('profile/address/update', views.UpdateProfileAddressView.as_view(), name='profile_update_address'),
    path('profile/address/delete', views.DeleteProfileAddressView.as_view(), name='profile_delete_address'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us_page'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_page'),
    path('faq/', views.FAQView.as_view(), name='faq_page'),
    path('about-project/', views.AboutProjectView.as_view(), name='about_project')
]
