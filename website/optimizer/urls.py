from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='optimizer-home'),
    path('about/', views.about, name='optimizer-about'),
    path('optimizer/', views.create_optimizer, name='optimizer-optimizer')
]