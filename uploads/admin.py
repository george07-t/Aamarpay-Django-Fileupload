from django.contrib import admin
from .models import FileUpload, ActivityLog

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'status', 'word_count', 'upload_time']
    list_filter = ['status', 'upload_time']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['upload_time', 'word_count']
    
    def has_delete_permission(self, request, obj=None):
        # Staff cannot delete user uploads
        return False

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['action', 'user__username']
    readonly_fields = ['timestamp', 'metadata']
    
    def has_delete_permission(self, request, obj=None):
        # Staff cannot delete activity logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Staff can only view activity logs
        return False