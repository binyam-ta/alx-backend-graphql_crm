#!/usr/bin/env python3

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import timedelta

GRAPHQL_URL = "http://localhost:8000/graphql"

def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes to confirm the CRM is alive"""

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/crm_heartbeat_log.txt"

    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    # Optional: check GraphQL 'hello' query
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        query {
            hello
        }
        """)
        result = client.execute(query)

        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL response: {result}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL error: {e}\n")


def send_order_reminders():
    """Queries pending orders (last 7 days) and logs reminders"""
    transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query PendingOrders($startDate: DateTime!) {
      orders(filter: {order_date_gte: $startDate}) {
        id
        customer {
          email
        }
        order_date
      }
    }
    """)

    start_date = (datetime.datetime.now() - timedelta(days=7)).isoformat()
    params = {"startDate": start_date}

    log_file = "/tmp/order_reminders_log.txt"

    try:
        result = client.execute(query, variable_values=params)
        orders = result.get("orders", [])

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            for order in orders:
                order_id = order["id"]
                email = order["customer"]["email"]
                f.write(f"[{timestamp}] Order ID: {order_id}, Customer Email: {email}\n")

        print("Order reminders processed!")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error sending order reminders: {e}\n")


def update_low_stock():
    """Executes UpdateLowStockProducts mutation for products with stock < 10"""

    transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
        updateLowStockProducts {
            updatedProducts {
                id
                name
                stock
            }
            message
        }
    }
    """)

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        result = client.execute(mutation)
        updated_products = result["updateLowStockProducts"]["updatedProducts"]

        with open(log_file, "a") as f:
            for product in updated_products:
                f.write(f"[{timestamp}] Product: {product['name']}, New Stock: {product['stock']}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error updating low stock products: {e}\n")
