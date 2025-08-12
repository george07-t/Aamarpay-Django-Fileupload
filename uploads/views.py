from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from payments.models import PaymentTransaction
from .models import FileUpload, ActivityLog
from .serializers import FileUploadSerializer, ActivityLogSerializer, FileUploadListSerializer
from .tasks import process_file_word_count
import os

class FileUploadAPIView(APIView):
    """API endpoint for file upload"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if user has completed payment
        has_payment = PaymentTransaction.objects.filter(
            user=request.user,
            status='completed'
        ).exists()
        
        if not has_payment:
            return Response(
                {'error': 'Payment required before uploading files'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            file_upload = serializer.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='file_uploaded',
                metadata={
                    'filename': file_upload.filename,
                    'file_size': file_upload.file_size,
                    'file_type': file_upload.file_type
                }
            )
            
            # Trigger Celery task for word counting
            process_file_word_count.delay(file_upload.id)
            
            return Response(
                {
                    'message': 'File uploaded successfully. Processing word count...',
                    'file_id': file_upload.id,
                    'filename': file_upload.filename
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDeleteAPIView(APIView):
    """API endpoint for file deletion"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, file_id, *args, **kwargs):
        try:
            file_upload = FileUpload.objects.get(id=file_id, user=request.user)
            
            # Log activity before deletion
            ActivityLog.objects.create(
                user=request.user,
                action='file_deleted',
                metadata={
                    'filename': file_upload.filename,
                    'file_size': file_upload.file_size,
                    'file_type': file_upload.file_type,
                    'word_count': file_upload.word_count
                }
            )
            
            filename = file_upload.filename
            file_upload.delete()
            
            return Response(
                {'message': f'File "{filename}" deleted successfully'},
                status=status.HTTP_200_OK
            )
            
        except FileUpload.DoesNotExist:
            return Response(
                {'error': 'File not found or you do not have permission to delete it'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error deleting file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_user_files(request):
    """List all files uploaded by the user"""
    files = FileUpload.objects.filter(user=request.user)
    serializer = FileUploadListSerializer(files, many=True)
    
    return Response({
        'files': serializer.data,
        'total_files': files.count(),
        'completed_files': files.filter(status='completed').count(),
        'processing_files': files.filter(status='processing').count(),
        'failed_files': files.filter(status='failed').count(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_user_activities(request):
    """List all activities by the user"""
    activities = ActivityLog.objects.filter(user=request.user)[:20]  # Last 20 activities
    serializer = ActivityLogSerializer(activities, many=True)
    
    return Response({
        'activities': serializer.data,
        'total_activities': ActivityLog.objects.filter(user=request.user).count()
    })


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def upload_file_view(request):
    """File upload page"""
    # Check if user has completed payment
    has_payment = PaymentTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).exists()
    
    if not has_payment:
        messages.warning(request, 'Please complete payment before uploading files.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        print(f"POST request received")
        print(f"FILES: {request.FILES}")
        print(f"POST data: {request.POST}")
        
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return render(request, 'upload.html', {'has_payment': has_payment})
        
        print(f"File received: {uploaded_file.name}, Size: {uploaded_file.size}")
        
        # Validate file extension
        allowed_extensions = ['.txt', '.docx']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            messages.error(request, 'Only .txt and .docx files are allowed.')
            return render(request, 'upload.html', {'has_payment': has_payment})
        
        # Validate file size (10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size cannot exceed 10MB.')
            return render(request, 'upload.html', {'has_payment': has_payment})
        
        try:
            # Create file upload record
            file_upload = FileUpload.objects.create(
                user=request.user,
                file=uploaded_file,
                filename=uploaded_file.name,
                file_size=uploaded_file.size,
                file_type=file_extension
            )
            
            print(f"FileUpload created: ID={file_upload.id}, Path={file_upload.file.path}")
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='file_uploaded',
                metadata={
                    'filename': file_upload.filename,
                    'file_size': file_upload.file_size,
                    'file_type': file_upload.file_type
                }
            )
            
            # Trigger Celery task
            task_result = process_file_word_count.delay(file_upload.id)
            print(f"Celery task triggered: {task_result.id}")
            
            messages.success(request, f'File "{uploaded_file.name}" uploaded successfully! Word count processing started.')
            return redirect('file_list')
            
        except Exception as e:
            print(f"Error creating FileUpload: {str(e)}")
            messages.error(request, f'Error uploading file: {str(e)}')
            return render(request, 'upload.html', {'has_payment': has_payment})
    
    context = {
        'user': request.user,
        'has_payment': has_payment,
    }
    return render(request, 'upload.html', context)


@login_required
def file_list_view(request):
    """File list page"""
    files = FileUpload.objects.filter(user=request.user)
    
    context = {
        'user': request.user,
        'files': files,
        'total_files': files.count(),
        'completed_files': files.filter(status='completed').count(),
        'processing_files': files.filter(status='processing').count(),
        'failed_files': files.filter(status='failed').count(),
        'total_words': sum(f.word_count for f in files.filter(status='completed')),
    }
    return render(request, 'files.html', context)


@login_required
def delete_file_view(request, file_id):
    """Delete file view"""
    try:
        file_upload = get_object_or_404(FileUpload, id=file_id, user=request.user)
        
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action='file_deleted',
            metadata={
                'filename': file_upload.filename,
                'file_size': file_upload.file_size,
                'file_type': file_upload.file_type,
                'word_count': file_upload.word_count
            }
        )
        
        filename = file_upload.filename
        file_upload.delete() 
        
        messages.success(request, f'File "{filename}" deleted successfully.')
        
    except Exception as e:
        messages.error(request, f'Error deleting file: {str(e)}')
    
    return redirect('file_list')