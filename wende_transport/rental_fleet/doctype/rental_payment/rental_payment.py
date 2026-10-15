import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RentalPayment(Document):
    def on_update(self):
        if self.owner and self.amount:
            owner = frappe.get_doc("Rental Owner", self.owner)
            owner.current_balance = max(0.0, flt(owner.current_balance) - flt(self.amount))
            owner.save(ignore_permissions=True)
