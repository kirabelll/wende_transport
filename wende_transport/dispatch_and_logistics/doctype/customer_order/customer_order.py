import frappe
from frappe.model.document import Document

class CustomerOrder(Document):
    def validate(self):
        self.check_customer_dispatch_block()
        self.calculate_rates_and_totals()

    def check_customer_dispatch_block(self):
        if self.customer:
            cust = frappe.get_doc("Customer", self.customer)
            if cust.dispatch_blocked:
                frappe.throw(f"Cannot process order: Customer {cust.company_name} is blocked ({cust.block_reason or 'credit limit/overdue balance'}).")

    def calculate_rates_and_totals(self):
        # Auto-fetch from active rate contract if rate not specified
        if not self.base_rate and self.customer:
            contracts = frappe.get_all("Rate Contract",
                filters={"customer": self.customer, "is_active": 1},
                fields=["rate_per_ton"],
                order_by="creation desc",
                limit=1
            )
            if contracts and contracts[0].rate_per_ton:
                self.base_rate = contracts[0].rate_per_ton

        active_rate = self.adjusted_rate or self.base_rate or 0
        qty = self.quantity or 0
        self.total_amount = qty * active_rate
        delivered = self.total_delivered or 0
        self.remaining_qty = max(0.0, qty - delivered)

    def update_delivery_progress(self):
        # Calculate sum of delivered tons and trips count from completed trips
        trips = frappe.get_all("Trip",
            filters={"order": self.name, "docstatus": ["!=", 2], "status": ["!=", "Cancelled"]},
            fields=["status", "delivered_quantity_tons"]
        )
        self.total_trips = len(trips)
        completed_trips = [t for t in trips if t.status == "Completed"]
        self.total_delivered = sum(t.delivered_quantity_tons or 0 for t in completed_trips)
        self.remaining_qty = max(0.0, (self.quantity or 0) - self.total_delivered)
        
        if len(completed_trips) >= len(trips) and len(trips) > 0 and self.remaining_qty <= 0:
            if self.status not in ["Delivered", "Invoiced", "Paid"]:
                self.status = "Delivered"

        self.save(ignore_permissions=True)
