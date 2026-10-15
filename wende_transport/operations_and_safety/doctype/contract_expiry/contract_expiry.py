import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class ContractExpiry(Document):
    def validate(self):
        if self.expiry_date and getdate(self.expiry_date) < getdate(nowdate()):
            self.status = "Expired"
