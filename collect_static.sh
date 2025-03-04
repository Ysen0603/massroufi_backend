#!/bin/bash

# Create static directory if it doesn't exist
mkdir -p static
# Collect static files
./.venv/bin/python manage.py collectstatic --noinput