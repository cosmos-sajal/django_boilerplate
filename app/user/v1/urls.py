from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterUserView, LoginUserView, GenerateOTPView, \
    PasswordResetMailView, PasswordResetView

app_name = 'user'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('generate/otp/', GenerateOTPView.as_view(), name='generate-otp'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('password_reset/mail/', PasswordResetMailView.as_view(),
         name='password-reset-mail'),
    path('password_reset/<str:uid>/',
         PasswordResetView.as_view(), name='password-reset')
]
