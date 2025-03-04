#!/bin/bash

# Install project dependencies
python -m pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p static
# Collect static files
python manage.py collectstatic --noinput