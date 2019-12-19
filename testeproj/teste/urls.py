from django.urls import path
from . import views

app_name = 'teste'
urlpatterns = [
    path('', views.index, name='index'),
]
