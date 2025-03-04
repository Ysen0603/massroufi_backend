from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ExpenseCategory, Transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'current_balance', 'is_superuser')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'is_superuser': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class ExpenseCategorySerializer(serializers.ModelSerializer):
    name_by_language = serializers.SerializerMethodField()

    def get_name_by_language(self, obj):
        request = self.context.get('request')
        language = request.headers.get('Accept-Language', 'en')[:2].lower() if request else 'en'
        return obj.get_name_by_language(language)

    class Meta:
        model = ExpenseCategory
        fields = ('id', 'name', 'name_fr', 'name_ar', 'name_by_language', 'icon', 'color')

class TransactionSerializer(serializers.ModelSerializer):
    category_details = ExpenseCategorySerializer(source='category', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'title', 'amount', 'category', 'category_details', 'type', 'date', 'notes', 'is_recurring')
        read_only_fields = ('user',)