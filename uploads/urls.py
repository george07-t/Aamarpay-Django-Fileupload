from django.urls import path
from . import views

app_name = 'uploads'

urlpatterns = [
    path('upload/', views.FileUploadAPIView.as_view(), name='api_upload_file'),
    path('files/', views.list_user_files, name='api_list_files'),
    path('activities/', views.list_user_activities, name='api_list_activities'),
    path('delete/<int:file_id>/', views.FileDeleteAPIView.as_view(), name='api_delete_file'),
]