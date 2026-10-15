import frappe
from frappe.utils import flt

def validate_customer_order(doc, method):
    doc.check_customer_dispatch_block()
    doc.calculate_rates_and_totals()

@frappe.whitelist()
def get_order_summary():
    orders = frappe.get_all("Customer Order",
        fields=["name", "customer", "order_type", "quantity", "total_delivered", "remaining_qty", "status", "total_amount"],
        order_by="creation desc"
    )
    return {
        "orders": orders,
        "total_active_orders": sum(1 for o in orders if o.status not in ["Delivered", "Invoiced", "Paid", "Rejected"]),
        "total_open_tonnage": sum(flt(o.remaining_qty) for o in orders if o.status not in ["Delivered", "Invoiced", "Paid", "Rejected"])
    }
