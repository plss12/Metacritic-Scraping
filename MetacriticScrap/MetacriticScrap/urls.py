#encoding:utf-8

from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.index),
   
]
