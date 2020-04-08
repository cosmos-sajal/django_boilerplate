from django.urls import path
from .views import RegisterUserView, LoginUserView, GenerateOTPView

app_name = 'user'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('generate/otp/', GenerateOTPView.as_view(), name='generate-otp'),
]
