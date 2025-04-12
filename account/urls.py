from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('userInfo/', views.currentUser, name='userInfo'),
    path('updateProfile/', views.updateProfile, name='updateProfile'),

    path('forgotPassword/', views.forgot_password, name='forgotPassword'),
    path('resetPassword/<str:token>', views.reset_password, name='resetPassword'),
]