from django.urls import path, include, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.client_login, name="login"),
    path('logout/', views.logout_client, name="logout"),
    path('', include('django.contrib.auth.urls')),
    path('reset_password/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('authentication:password_reset_done')), name="reset_password"),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]