from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect  # Add this import
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view),
    
    # Payment URLs
    path('initiate-payment/', views.initiate_payment_view, name='initiate_payment'),
    
    # Functional URLs 
    path('upload/', views.upload_file_view, name='upload_file'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('files/', views.file_list_view, name='file_list'),
    
    path('admin/', admin.site.urls),
    path('api/payments/', include('payments.urls')),
    path('api/uploads/', include('uploads.urls')),
    path('api/auth/', include('authentication.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar URLs
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns