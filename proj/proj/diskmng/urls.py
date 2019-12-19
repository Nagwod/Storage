from django.urls import path
from . import views

app_name = 'diskmng'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('storage/', views.storage, name='storage'),
    path('du/', views.du, name='du'),
]
