from django.urls import path
from . import views

app_name = 'vectordb'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
]
