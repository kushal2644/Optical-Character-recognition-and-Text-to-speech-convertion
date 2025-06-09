from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ForgotPasswordView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('capture_image/', views.capture_image, name='capture_image'),  # Endpoint to capture and process the image
    path('subscription/', views.subscription_view, name='subscription'),
    path('profile/', views.profile_view, name='profile'),
    path('help/', views.help_view, name='help'),
    path('voice/', views.voice_view, name='voice'),
    
    path('settings/', views.settings_view, name='settings'),

    
  
    

    
        

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
