from django.core.management import execute_from_command_line
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'massroufi_backend.settings')

import django
django.setup()

from authentication.models import ExpenseCategory

def create_categories():
    # First clear existing categories if needed
    ExpenseCategory.objects.all().delete()
    
    categories = [
        ExpenseCategory(name='Food', name_fr='Alimentation', name_ar='الطعام', icon='restaurant-outline', color='#00FF99'),
        ExpenseCategory(name='Housing', name_fr='Logement', name_ar='السكن', icon='home-outline', color='#0099FF'),
        ExpenseCategory(name='Leisure', name_fr='Loisirs', name_ar='الترفيه', icon='game-controller-outline', color='#BB86FC'),
        ExpenseCategory(name='Transport', name_fr='Transport', name_ar='النقل', icon='car-outline', color='#FF6B6B'),
        ExpenseCategory(name='Other', name_fr='Autre', name_ar='آخر', icon='ellipsis-horizontal-outline', color='#808080')
    ]
    ExpenseCategory.objects.bulk_create(categories)
    print('Categories created successfully in Supabase database!')

if __name__ == '__main__':
    create_categories()
