# import re
# import graphene
# from django.core.exceptions import ValidationError
# from django.db import transaction
# from django.utils import timezone
# from graphene_django.types import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
# from .models import Customer, Product, Order
# from .filters import CustomerFilter, ProductFilter, OrderFilter

# # ---------------------------
# # Object Types
# # ---------------------------
# class CustomerType(DjangoObjectType):
#     class Meta:
#         model = Customer
#         interfaces = (graphene.relay.Node,)

# class ProductType(DjangoObjectType):
#     class Meta:
#         model = Product
#         interfaces = (graphene.relay.Node,)

# class OrderType(DjangoObjectType):
#     class Meta:
#         model = Order
#         interfaces = (graphene.relay.Node,)


# # ---------------------------
# # Mutations
# # ---------------------------
# # Create Customer
# class CreateCustomer(graphene.Mutation):
#     customer = graphene.Field(CustomerType)
#     message = graphene.String()

#     class Arguments:
#         name = graphene.String(required=True)
#         email = graphene.String(required=True)
#         phone = graphene.String()

#     def mutate(self, info, name, email, phone=None):
#         if Customer.objects.filter(email=email).exists():
#             raise ValidationError("Email already exists")
        
#         if phone:
#             pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
#             if not re.match(pattern, phone):
#                 raise ValidationError("Invalid phone format")
        
#         customer = Customer(name=name, email=email, phone=phone)
#         customer.save()
#         return CreateCustomer(customer=customer, message="Customer created successfully!")


# # Bulk Create Customers
# class CustomerInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     email = graphene.String(required=True)
#     phone = graphene.String()

# class BulkCreateCustomers(graphene.Mutation):
#     customers = graphene.List(CustomerType)
#     errors = graphene.List(graphene.String)

#     class Arguments:
#         input = graphene.List(CustomerInput, required=True)

#     @classmethod
#     @transaction.atomic
#     def mutate(cls, root, info, input):
#         created_customers = []
#         errors = []

#         for c in input:
#             try:
#                 if Customer.objects.filter(email=c.email).exists():
#                     raise ValidationError(f"Email {c.email} already exists")
                
#                 if c.phone:
#                     pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
#                     if not re.match(pattern, c.phone):
#                         raise ValidationError(f"Invalid phone format: {c.phone}")
                
#                 customer = Customer(name=c.name, email=c.email, phone=c.phone)
#                 customer.full_clean()
#                 customer.save()
#                 created_customers.append(customer)
#             except Exception as e:
#                 errors.append(str(e))

#         return BulkCreateCustomers(customers=created_customers, errors=errors)


# # Create Product
# class CreateProduct(graphene.Mutation):
#     product = graphene.Field(ProductType)

#     class Arguments:
#         name = graphene.String(required=True)
#         price = graphene.Float(required=True)
#         stock = graphene.Int()

#     def mutate(self, info, name, price, stock=0):
#         if price <= 0:
#             raise ValidationError("Price must be positive")
#         if stock < 0:
#             raise ValidationError("Stock cannot be negative")

#         product = Product(name=name, price=price, stock=stock)
#         product.save()
#         return CreateProduct(product=product)


# # Create Order
# class CreateOrder(graphene.Mutation):
#     order = graphene.Field(OrderType)

#     class Arguments:
#         customer_id = graphene.ID(required=True)
#         product_ids = graphene.List(graphene.ID, required=True)
#         order_date = graphene.DateTime()

#     def mutate(self, info, customer_id, product_ids, order_date=None):
#         try:
#             customer = Customer.objects.get(id=customer_id)
#         except Customer.DoesNotExist:
#             raise ValidationError("Customer ID invalid")

#         products = Product.objects.filter(id__in=product_ids)
#         if not products.exists():
#             raise ValidationError("No valid products selected")

#         if order_date is None:
#             order_date = timezone.now()

#         order = Order(customer=customer, order_date=order_date)
#         order.save()
#         order.products.set(products)
#         order.save()  # calculates total_amount

#         return CreateOrder(order=order)


# # ---------------------------
# # Mutation Class
# # ---------------------------
# class Mutation(graphene.ObjectType):
#     create_customer = CreateCustomer.Field()
#     bulk_create_customers = BulkCreateCustomers.Field()
#     create_product = CreateProduct.Field()
#     create_order = CreateOrder.Field()


# # ---------------------------
# # Query with Filters
# # ---------------------------
# class Query(graphene.ObjectType):
#     all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
#     all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
#     all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

import graphene
from graphene_django import DjangoObjectType
from crm.models import Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(root, info):
        # Find products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products_list = []

        for product in low_stock_products:
            product.stock += 10  # Restock by 10
            product.save()
            updated_products_list.append(product)

        return UpdateLowStockProducts(
            updated_products=updated_products_list,
            message=f"{len(updated_products_list)} products restocked successfully"
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
