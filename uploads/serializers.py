from rest_framework import serializers
from .models import FileUpload, ActivityLog
from django.core.validators import FileExtensionValidator
import os

class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'docx'])],
        write_only=True
    )
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)

    class Meta:
        model = FileUpload
        fields = [
            'id', 'filename', 'upload_time', 'status', 
            'word_count', 'file_size', 'file_size_display', 
            'file_type', 'file'
        ]
        read_only_fields = [
            'id', 'filename', 'upload_time', 'status', 
            'word_count', 'file_size', 'file_type'
        ]

    def validate_file(self, value):
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        # Check file extension
        allowed_extensions = ['.txt', '.docx']
        file_extension = os.path.splitext(value.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError("Only .txt and .docx files are allowed.")
        
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FileUploadListSerializer(serializers.ModelSerializer):
    """Serializer for listing files without file field"""
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)

    class Meta:
        model = FileUpload
        fields = [
            'id', 'filename', 'upload_time', 'status', 
            'word_count', 'file_size', 'file_size_display', 
            'file_type'
        ]


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'metadata', 'timestamp']
        read_only_fields = ['id', 'timestamp']