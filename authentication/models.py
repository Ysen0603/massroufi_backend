from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    current_balance = models.DecimalField(_('current balance'), max_digits=10, decimal_places=2, default=0.00)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class ExpenseCategory(models.Model):
    name = models.CharField(_('name'), max_length=50)
    name_fr = models.CharField(_('name (French)'), max_length=50)
    name_ar = models.CharField(_('name (Arabic)'), max_length=50)
    icon = models.CharField(_('icon'), max_length=50)
    color = models.CharField(_('color'), max_length=7)  # Hex color code

    def __str__(self):
        return self.name

    def get_name_by_language(self, language):
        if language == 'fr':
            return self.name_fr
        elif language == 'ar':
            return self.name_ar
        return self.name  # Default to English

    class Meta:
        verbose_name = _('expense category')
        verbose_name_plural = _('expense categories')

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('expense', _('Expense')),
        ('income', _('Income')),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(_('title'), max_length=100)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(_('type'), max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(_('date'))
    notes = models.TextField(_('notes'), blank=True, null=True)
    is_recurring = models.BooleanField(_('is recurring'), default=False)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Update user's current balance when a transaction is saved
        if self.type == 'income':
            self.user.current_balance += self.amount
        else:  # expense
            self.user.current_balance -= self.amount
        self.user.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update user's current balance when a transaction is deleted
        if self.type == 'income':
            self.user.current_balance -= self.amount
        else:  # expense
            self.user.current_balance += self.amount
        self.user.save()
        super().delete(*args, **kwargs)
