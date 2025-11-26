from django.urls import path
from .views import loan_dashboard, apply_loan, repay_loan_view
from loans import views

app_name = 'loans'

urlpatterns = [
    path('', loan_dashboard, name='dashboard'),
    path('apply/', apply_loan, name='apply'),
    path("repay/<int:loan_id>/", views.repay_loan_view, name="repay_loan"),

]
