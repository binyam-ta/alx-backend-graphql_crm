import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

# Seed some initial products
products = [
    {"name": "Laptop", "price": 999.99, "stock": 10},
    {"name": "Mouse", "price": 25.50, "stock": 50},
]

for p in products:
    Product.objects.get_or_create(**p)

print("Seeding complete!")
