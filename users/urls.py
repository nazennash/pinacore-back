from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('request-otp/', views.RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('seller-login/', views.SellerLoginView.as_view(), name='seller-login'),
    path('seller-register/', views.RegisterSellerView.as_view(), name='seller-register'),
]
