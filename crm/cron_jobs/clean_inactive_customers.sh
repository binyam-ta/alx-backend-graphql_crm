#!/bin/bash
# Delete inactive customers with no orders in the past year

PROJECT_DIR="/home/binyam/Documents/alx-backend-graphql_crm"
cd $PROJECT_DIR

# Activate virtual environment
source venv/bin/activate

# Set correct Django settings module
export DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings

# Run cleanup and log results
python manage.py shell <<EOF
from django.utils import timezone
from crm.models import Customer
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=365)
deleted_count, _ = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff_date).delete()

print(deleted_count) 

with open("/tmp/customer_cleanup_log.txt", "a") as log:
    log.write(f"{timezone.now()} - Deleted {deleted_count} inactive customers.\n")
EOF
