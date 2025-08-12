from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from payments.models import PaymentTransaction
from uploads.models import FileUpload, ActivityLog
from uploads.tasks import process_file_word_count
import os
from uploads.models import FileUpload, ActivityLog
from django.shortcuts import get_object_or_404


def home_view(request):
    """Home page with MVT pattern"""
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    """Dashboard page with MVT pattern"""
    # Check if user has completed payment
    has_payment = PaymentTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).exists()
    
    # Get user's recent transactions (limit to 5 for dashboard)
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'user': request.user,
        'has_payment': has_payment,
        'transactions': transactions,
        'transaction_count': transactions.count(),
    }
    return render(request, 'dashboard.html', context)

@login_required
def transaction_list_view(request):
    """Full transaction list page"""
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    context = {
        'user': request.user,
        'transactions': transactions,
        'total_transactions': transactions.count(),
        'completed_transactions': transactions.filter(status='completed').count(),
        'pending_transactions': transactions.filter(status='pending').count(),
        'failed_transactions': transactions.filter(status='failed').count(),
    }
    return render(request, 'transactions.html', context)

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


def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'login.html')

def register_view(request):
    """Register page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'register.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'Username already exists. Please choose a different username.')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'register.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def initiate_payment_view(request):
    """Initiate payment via web form"""
    # Check if user already has a successful payment
    has_payment = PaymentTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).exists()
    
    if has_payment:
        messages.info(request, 'You have already made a successful payment and can upload files.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        from payments.services import AamarPayService
        
        amount = 100.00
        aamarpay_service = AamarPayService()
        result = aamarpay_service.initiate_payment(request.user, amount)
        
        if result['success']:
            # Redirect to aamarPay
            return redirect(result['payment_url'])
        else:
            messages.error(request, result['message'])
            return redirect('dashboard')
    
    return redirect('dashboard')