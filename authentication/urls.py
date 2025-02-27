from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('transactions-summary/', views.transactions_summary, name='transactions-summary'),
    path('update-balance/', views.update_balance, name='update-balance'),
    path('expense-categories/', views.expense_categories, name='expense-categories'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction-detail'),
    path('expenses/', views.expenses, name='expenses'),
    path('recent-transactions/', views.recent_transactions, name='recent-transactions'),
]