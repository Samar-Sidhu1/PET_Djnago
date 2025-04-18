from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pets/', views.pets, name='pets'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login_user'),
    path('logout/', views.logout_view, name='logout'),
]