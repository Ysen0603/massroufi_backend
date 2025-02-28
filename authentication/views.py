from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal
from .serializers import UserSerializer, ExpenseCategorySerializer, TransactionSerializer
from .models import Transaction, ExpenseCategory

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    try:
        user = User.objects.get(email=data['email'])
        if not user.check_password(data['password']):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_balance(request):
    try:
        new_balance = request.data.get('balance')
        if new_balance is None:
            return Response({'error': 'Balance is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_balance = Decimal(str(new_balance))
        except:
            return Response({'error': 'Invalid balance amount'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.current_balance = new_balance
        user.save()

        return Response({
            'current_balance': user.current_balance
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions_summary(request):
    try:
        user = request.user
        if not user:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            
        income = Transaction.objects.filter(user=user, type='income').aggregate(total=Sum('amount'))['total'] or 0
        expenses = Transaction.objects.filter(user=user, type='expense').aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'income': float(income),
            'expenses': float(expenses)
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expense_categories(request):
    if request.method == 'GET':
        categories = ExpenseCategory.objects.all()
        serializer = ExpenseCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ExpenseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transactions(request):
    if request.method == 'GET':
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk, user=request.user)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Calculate total income
    total_income = Transaction.objects.filter(
        user=user,
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Calculate total expenses
    total_expenses = Transaction.objects.filter(
        user=user,
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        'income': total_income,
        'expenses': total_expenses,
        'current_balance': user.current_balance
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expenses(request):
    if request.method == 'GET':
        expenses = Transaction.objects.filter(user=request.user, type='expense')
        serializer = TransactionSerializer(expenses, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        data['type'] = 'expense'
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_distribution(request):
    # Get all categories first
    categories = ExpenseCategory.objects.all()
    
    # Get user's current balance
    current_balance = request.user.current_balance

    if current_balance == 0:
        # If balance is 0, return all categories with 0%
        distribution = [{
            'category': category.name,
            'name': category.name,
            'name_fr': category.name_fr,
            'name_ar': category.name_ar,
            'name_by_language': category.get_name_by_language(request.headers.get('Accept-Language', 'en')[:2].lower()),
            'percentage': 0,
            'color': category.color,
            'icon': category.icon,
            'amount': 0
        } for category in categories]
        return Response(distribution)

    # Get expenses by category
    expenses_by_category = Transaction.objects.filter(
        user=request.user,
        type='expense'
    ).select_related('category').values('category').annotate(
        total_amount=Sum('amount')
    )

    # Create a dictionary of category IDs to their total amounts
    category_amounts = {expense['category']: expense['total_amount'] 
                       for expense in expenses_by_category if expense['category'] is not None}

    # Calculate percentages based on current balance and format response for all categories
    distribution = []
    language = request.headers.get('Accept-Language', 'en')[:2].lower()
    for category in categories:
        amount = float(category_amounts.get(category.id, 0))
        # Calculate percentage based on current balance instead of total expenses
        percentage = (amount / float(current_balance) * 100) if current_balance > 0 else 0
        distribution.append({
            'category': category.name,
            'name': category.name,
            'name_fr': category.name_fr,
            'name_ar': category.name_ar,
            'name_by_language': category.get_name_by_language(language),
            'percentage': round(percentage, 2),
            'color': category.color,
            'icon': category.icon,
            'amount': amount
        })

    return Response(distribution)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_transactions(request):
    try:
        user = request.user
        transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

