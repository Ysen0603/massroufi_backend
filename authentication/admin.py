from django.contrib import admin
from .models import CustomUser, ExpenseCategory, Transaction

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'current_balance', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_fr', 'name_ar', 'icon', 'color')
    search_fields = ('name', 'name_fr', 'name_ar')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'type', 'date', 'user', 'is_recurring')
    list_filter = ('type', 'is_recurring', 'category')
    search_fields = ('title', 'notes')
    date_hierarchy = 'date'
