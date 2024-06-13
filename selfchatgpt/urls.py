# blog/urls.py
from django.urls import path
from django.contrib import admin
from . import views

app_name = 'selfchatgpt'
urlpatterns = [
    path('', views.index, name='index'),
    path('chat', views.chat, name='chat'),
    path('history', views.show_log, name='log'),
    path('search_log', views.search_log, name='search-history'),
]
