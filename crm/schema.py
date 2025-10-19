import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re

# --- Object Types ---
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        
        # Optional phone validation
        if phone:
            pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
            if not re.match(pattern, phone):
                raise ValidationError("Invalid phone format")
        
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        for c in input:
            try:
                if Customer.objects.filter(email=c.email).exists():
                    raise ValidationError(f"Email {c.email} already exists")
                
                if c.phone:
                    pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
                    if not re.match(pattern, c.phone):
                        raise ValidationError(f"Invalid phone format: {c.phone}")
                
                customer = Customer(name=c.name, email=c.email, phone=c.phone)
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer ID invalid")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise ValidationError("No valid products selected")

        if order_date is None:
            order_date = timezone.now()

        order = Order(customer=customer, order_date=order_date)
        order.save()
        order.products.set(products)
        order.save()  # calculates total_amount

        return CreateOrder(order=order)
