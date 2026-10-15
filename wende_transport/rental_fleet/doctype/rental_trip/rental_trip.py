import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RentalTrip(Document):
    def validate(self):
        qty = flt(self.quantity_tons)
        rate = flt(self.rate_per_ton)
        self.customer_revenue = qty * rate
        payable = flt(self.rental_payable)
        self.gross_margin = self.customer_revenue - payable

    def on_update(self):
        if self.status == "Completed" and self.rental_vehicle and self.rental_payable:
            rv = frappe.get_doc("Rental Vehicle", self.rental_vehicle)
            if rv.owner:
                owner = frappe.get_doc("Rental Owner", rv.owner)
                owner.current_balance = (owner.current_balance or 0) + flt(self.rental_payable)
                owner.save(ignore_permissions=True)
