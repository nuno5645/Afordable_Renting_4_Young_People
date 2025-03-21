from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Password management
    path('password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('password/reset/request/', views.RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.ResetPasswordView.as_view(), name='password_reset_confirm'),
] 