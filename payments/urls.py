from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/fail/', views.PaymentFailView.as_view(), name='payment_fail'),
    path('payment/cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('check-status/', views.check_payment_status, name='check_payment_status'),
]