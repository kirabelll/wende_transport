import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class CompanyLegalDocument(Document):
    def validate(self):
        if self.expiry_date:
            if getdate(self.expiry_date) < getdate(nowdate()):
                self.status = "Expired"
            else:
                if self.status != "Pending Renewal":
                    self.status = "Active"
