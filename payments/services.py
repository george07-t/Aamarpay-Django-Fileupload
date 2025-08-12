import requests
import json
import uuid
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from .models import PaymentTransaction
import logging

logger = logging.getLogger(__name__)

class AamarPayService:
    def __init__(self):
        self.store_id = settings.AAMARPAY_STORE_ID
        self.signature_key = settings.AAMARPAY_SIGNATURE_KEY
        self.sandbox_url = settings.AAMARPAY_SANDBOX_URL
        self.success_url = settings.AAMARPAY_SUCCESS_URL
        self.fail_url = settings.AAMARPAY_FAIL_URL
        self.cancel_url = settings.AAMARPAY_CANCEL_URL
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"TXN_{timestamp}_{unique_id}"
    
    def initiate_payment(self, user: User, amount: float = 100.00):
        """
        Initiate payment with aamarPay
        """
        transaction_id = self.generate_transaction_id()
        
        # Create payment transaction record
        payment_transaction = PaymentTransaction.objects.create(
            user=user,
            transaction_id=transaction_id,
            amount=amount,
            status='pending'
        )
        
        # Prepare payload for aamarPay
        payload = {
            "store_id": self.store_id,
            "signature_key": self.signature_key,
            "tran_id": transaction_id,
            "amount": str(amount),
            "currency": "BDT",
            "desc": "File Upload Payment - aamarPay Integration",
            "cus_name": user.get_full_name() or user.username,
            "cus_email": user.email or f"{user.username}@example.com",
            "cus_phone": "+8801700000000",  # Default phone
            "success_url": self.success_url,
            "fail_url": self.fail_url,
            "cancel_url": self.cancel_url,
            "type": "json",
            "cus_add1": "Dhaka",
            "cus_city": "Dhaka",
            "cus_state": "Dhaka",
            "cus_country": "Bangladesh",
            "opt_a": str(user.id),  # Store user ID for reference
        }
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Initiating payment for user {user.username}, transaction {transaction_id}")
            
            response = requests.post(
                self.sandbox_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            response_data = response.json()
            
            # Update transaction with gateway response
            payment_transaction.gateway_response = response_data
            payment_transaction.save()
            
            logger.info(f"aamarPay response: {response_data}")
            
            if response_data.get('result') == 'true':
                payment_url = response_data.get('payment_url')
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'transaction_id': transaction_id,
                    'message': 'Payment initiated successfully'
                }
            else:
                payment_transaction.status = 'failed'
                payment_transaction.save()
                return {
                    'success': False,
                    'message': 'Failed to initiate payment',
                    'error': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            payment_transaction.status = 'failed'
            payment_transaction.gateway_response = {'error': str(e)}
            payment_transaction.save()
            
            return {
                'success': False,
                'message': 'Payment gateway connection failed',
                'error': str(e)
            }
    
    def handle_payment_callback(self, callback_data):
        """
        Handle aamarPay callback after payment
        """
        try:
            transaction_id = callback_data.get('mer_txnid')
            status_code = callback_data.get('status_code')
            pay_status = callback_data.get('pay_status')
            pg_txnid = callback_data.get('pg_txnid')
            
            logger.info(f"Processing callback for transaction {transaction_id}")
            
            # Find the payment transaction
            try:
                payment_transaction = PaymentTransaction.objects.get(
                    transaction_id=transaction_id
                )
            except PaymentTransaction.DoesNotExist:
                logger.error(f"Transaction {transaction_id} not found")
                return {
                    'success': False,
                    'message': 'Transaction not found'
                }
            
            # Update transaction with callback data
            payment_transaction.gateway_response.update(callback_data)
            payment_transaction.aamarpay_tran_id = pg_txnid
            
            # Check payment status
            if status_code == '2' and pay_status == 'Successful':
                payment_transaction.status = 'completed'
                logger.info(f"Payment successful for transaction {transaction_id}")
                
                # Log activity
                from uploads.models import ActivityLog
                ActivityLog.objects.create(
                    user=payment_transaction.user,
                    action='payment_completed',
                    metadata={
                        'transaction_id': transaction_id,
                        'amount': str(payment_transaction.amount),
                        'pg_txnid': pg_txnid
                    }
                )
                
            elif status_code == '7':
                payment_transaction.status = 'failed'
                logger.info(f"Payment failed for transaction {transaction_id}")
            else:
                payment_transaction.status = 'cancelled'
                logger.info(f"Payment cancelled for transaction {transaction_id}")
            
            payment_transaction.save()
            
            return {
                'success': True,
                'transaction': payment_transaction,
                'message': f'Payment {payment_transaction.status}'
            }
            
        except Exception as e:
            logger.error(f"Callback processing failed: {str(e)}")
            return {
                'success': False,
                'message': 'Callback processing failed',
                'error': str(e)
            }