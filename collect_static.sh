#!/bin/bash

# Create static directory if it doesn't exist
mkdir -p static
# Collect static files
/opt/conda/bin/python manage.py collectstatic --noinput