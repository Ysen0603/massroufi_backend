from django.core.management import execute_from_command_line
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'massroufi_backend.settings')

import django
django.setup()

from authentication.models import ExpenseCategory

def create_categories():
    categories = [
        ExpenseCategory(name='Alimentation', icon='restaurant-outline', color='#00FF99'),
        ExpenseCategory(name='Logement', icon='home-outline', color='#0099FF'),
        ExpenseCategory(name='Loisirs', icon='game-controller-outline', color='#BB86FC'),
        ExpenseCategory(name='Transport', icon='car-outline', color='#FF6B6B'),
        ExpenseCategory(name='Autre', icon='ellipsis-horizontal-outline', color='#808080')
    ]
    ExpenseCategory.objects.bulk_create(categories)
    print('Categories created successfully!')

if __name__ == '__main__':
    create_categories()