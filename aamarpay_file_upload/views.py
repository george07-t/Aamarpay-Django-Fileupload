from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from payments.models import PaymentTransaction

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
    """File list page (placeholder for now)"""
    # This will be implemented when upload functionality is added
    context = {
        'user': request.user,
        'files': [],  # Empty for now
        'message': 'File upload functionality will be implemented soon.'
    }
    return render(request, 'files.html', context)

@login_required 
def upload_file_view(request):
    """File upload page (placeholder for now)"""
    # Check if user has completed payment
    has_payment = PaymentTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).exists()
    
    if not has_payment:
        messages.warning(request, 'Please complete payment before uploading files.')
        return redirect('dashboard')
    
    context = {
        'user': request.user,
        'has_payment': has_payment,
        'message': 'File upload functionality will be implemented soon.'
    }
    return render(request, 'upload.html', context)

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
                
                # Redirect to next URL if provided, otherwise dashboard
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