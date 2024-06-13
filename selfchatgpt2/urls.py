from django.urls import path
from django.contrib import admin
from selfchatgpt2 import views
from selfchatgpt2.views import ChatbotView

app_name = 'selfchatgpt2'
urlpatterns = [

    path('', views.index, name='index'),
    path('chat', ChatbotView.as_view(), name='chatbot'),
]
