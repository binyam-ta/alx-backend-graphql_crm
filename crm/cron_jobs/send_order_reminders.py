#!/usr/bin/env python3
"""
Script to query pending orders from GraphQL API and log reminders
"""

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL query for orders in the last 7 days
query = gql(
    """
    query PendingOrders($startDate: DateTime!) {
      orders(filter: {order_date_gte: $startDate}) {
        id
        customer {
          email
        }
        order_date
      }
    }
    """
)

# Calculate 7 days ago
start_date = (datetime.now() - timedelta(days=7)).isoformat()

params = {"startDate": start_date}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log each order
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            log_file.write(f"[{timestamp}] Order ID: {order_id}, Customer Email: {email}\n")

    print("Order reminders processed!")

except Exception as e:
    print(f"Error querying GraphQL API: {e}")
