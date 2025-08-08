from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['transaction_id', 'user__username', 'user__email']
    readonly_fields = ['transaction_id', 'timestamp', 'gateway_response']
    
    def has_delete_permission(self, request, obj=None):
        # Staff cannot delete payment transactions
        return False
    
    def has_change_permission(self, request, obj=None):
        # Staff can only view, not edit payment data
        return request.user.is_superuser