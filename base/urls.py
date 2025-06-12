from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('os/', views.os_library, name='os_library'),
    path('save_vm/', views.Save_vm, name='save_vm'),
    path('profile/', views.profile, name='profile'),
    path('vm/viewer/', views.start_vm, name='start_vm'),
]