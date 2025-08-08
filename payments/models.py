from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_response = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # aamarPay specific fields
    aamarpay_tran_id = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=3, default='BDT')
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.user.username} - {self.status}"