import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RevenueShareContract(Document):
    def validate(self):
        owner_p = flt(self.owner_share_percent)
        comp_p = flt(self.company_share_percent)
        if (owner_p + comp_p) != 100.0:
            frappe.throw(f"Total percentage shares must equal 100%. (Current sum: {owner_p + comp_p}%)")
