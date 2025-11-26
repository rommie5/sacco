from django.urls import path
from .views import deposit_history_view, deposit_view, stripe_webhook,account_view,deposit_success,transaction_history_view

app_name = 'savings'

urlpatterns = [
    path('deposit/', deposit_view, name='deposit'),
    path('deposit/webhook/', stripe_webhook, name='stripe-webhook'),
    path("deposit/success/", deposit_success, name="deposit_success"),
    path('account/', account_view, name='account'),
    path('transactions/', transaction_history_view, name='transaction_history'),
    path('deposit/history/', deposit_history_view, name='deposit_history'),  # ✅ name here


]
