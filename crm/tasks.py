import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"

@shared_task
def generate_crm_report():
    """Generates a weekly CRM report with total customers, orders, and revenue"""

    transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        customers {
            id
        }
        orders {
            id
            totalamount
        }
    }
    """)

    try:
        result = client.execute(query)
        customers = result.get("customers", [])
        orders = result.get("orders", [])

        total_customers = len(customers)
        total_orders = len(orders)
        total_revenue = sum([order["totalamount"] for order in orders])

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = "/tmp/crm_report_log.txt"

        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n")

    except Exception as e:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{timestamp} - Error generating report: {e}\n")
