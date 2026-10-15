import frappe
from frappe.model.document import Document
from frappe.utils import flt

class BrokerCommission(Document):
    def validate(self):
        if self.commission_type == "Percentage" and self.rate and self.trip_revenue:
            self.amount = round(flt(self.trip_revenue) * (flt(self.rate) / 100.0), 2)

    def on_update(self):
        if self.broker:
            b = frappe.get_doc("Transport Broker", self.broker)
            commissions = frappe.get_all("Broker Commission", filters={"broker": self.broker}, fields=["amount", "status"])
            total_earned = sum(c.amount for c in commissions if c.status in ["Approved", "Paid"])
            total_paid = sum(c.amount for c in commissions if c.status == "Paid")
            b.total_earned = total_earned
            b.total_paid = total_paid
            b.balance = total_earned - total_paid
            b.save(ignore_permissions=True)
