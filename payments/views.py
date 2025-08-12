from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .models import PaymentTransaction
from .serializers import (
    PaymentInitiateSerializer, 
    PaymentTransactionSerializer,
    PaymentCallbackSerializer
)
from .services import AamarPayService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    POST /api/payments/initiate-payment/
    Initiate payment with aamarPay
    """
    serializer = PaymentInitiateSerializer(data=request.data)
    
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount', 100.00)
        
        # Check if user already has a successful payment
        existing_payment = PaymentTransaction.objects.filter(
            user=request.user,
            status='completed'
        ).exists()
        
        if existing_payment:
            return Response({
                'message': 'You have already made a successful payment',
                'can_upload': True
            }, status=status.HTTP_200_OK)
        
        # Initiate payment
        aamarpay_service = AamarPayService()
        result = aamarpay_service.initiate_payment(request.user, amount)
        
        if result['success']:
            return Response({
                'success': True,
                'payment_url': result['payment_url'],
                'transaction_id': result['transaction_id'],
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message'],
                'error': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):
    """
    GET/POST /api/payments/payment/success/
    Handle aamarPay success callback
    """
    def post(self, request):
        try:
            # Parse callback data
            if request.content_type == 'application/json':
                callback_data = json.loads(request.body)
            else:
                callback_data = dict(request.POST.items())
            
            logger.info(f"Payment success callback received: {callback_data}")
            
            # Process callback
            aamarpay_service = AamarPayService()
            result = aamarpay_service.handle_payment_callback(callback_data)
            
            if result['success']:
                transaction = result['transaction']
                
                if transaction.status == 'completed':
                    return redirect('/dashboard/?payment=success')
                else:
                    return redirect('/dashboard/?payment=failed')
            else:
                return redirect('/dashboard/?payment=error')
                
        except Exception as e:
            logger.error(f"Payment success callback error: {str(e)}")
            return redirect('/dashboard/?payment=error')
    
    def get(self, request):
        return JsonResponse({
            'message': 'Payment success endpoint',
            'method': 'GET'
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailView(View):
    """
    GET/POST /api/payments/payment/fail/
    Handle aamarPay fail callback
    """
    def post(self, request):
        try:
            if request.content_type == 'application/json':
                callback_data = json.loads(request.body)
            else:
                callback_data = dict(request.POST.items())
            
            logger.info(f"Payment fail callback received: {callback_data}")
            
            # Process callback
            aamarpay_service = AamarPayService()
            result = aamarpay_service.handle_payment_callback(callback_data)
            
            return redirect('/dashboard/?payment=failed')
            
        except Exception as e:
            logger.error(f"Payment fail callback error: {str(e)}")
            return redirect('/dashboard/?payment=error')
    
    def get(self, request):
        return JsonResponse({
            'message': 'Payment failed endpoint',
            'method': 'GET'
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCancelView(View):
    """
    GET/POST /api/payments/payment/cancel/
    Handle aamarPay cancel callback
    """
    def post(self, request):
        try:
            if request.content_type == 'application/json':
                callback_data = json.loads(request.body)
            else:
                callback_data = dict(request.POST.items())
            
            logger.info(f"Payment cancel callback received: {callback_data}")
            
            # Process callback
            aamarpay_service = AamarPayService()
            result = aamarpay_service.handle_payment_callback(callback_data)
            
            return redirect('/dashboard/?payment=cancelled')
            
        except Exception as e:
            logger.error(f"Payment cancel callback error: {str(e)}")
            return redirect('/dashboard/?payment=error')
    
    def get(self, request):
        return JsonResponse({
            'message': 'Payment cancelled endpoint',
            'method': 'GET'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    """
    GET /api/payments/transactions/
    List user's payment transactions
    """
    transactions = PaymentTransaction.objects.filter(user=request.user)
    serializer = PaymentTransactionSerializer(transactions, many=True)
    
    return Response({
        'transactions': serializer.data,
        'count': transactions.count()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request):
    """
    GET /api/payments/check-status/
    Check if user can upload files
    """
    has_payment = PaymentTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).exists()
    
    return Response({
        'can_upload': has_payment,
        'user': request.user.username,
        'message': 'You can upload files' if has_payment else 'Payment required to upload files'
    }, status=status.HTTP_200_OK)