from rest_framework import serializers
from .models import PaymentTransaction
from django.contrib.auth.models import User

class PaymentInitiateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'amount', 'status', 
            'timestamp', 'currency', 'aamarpay_tran_id'
        ]
        read_only_fields = ['id', 'timestamp']

class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for aamarPay callback data"""
    pg_txnid = serializers.CharField()
    mer_txnid = serializers.CharField()
    pay_status = serializers.CharField()
    status_code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    cus_name = serializers.CharField(required=False)
    cus_email = serializers.CharField(required=False)
    cus_phone = serializers.CharField(required=False)