import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RevenueShareSettlement(Document):
    def validate(self):
        rev = flt(self.total_revenue)
        exp = flt(self.total_expenses)
        self.net_income = rev - exp

        if self.contract:
            c = frappe.get_doc("Revenue Share Contract", self.contract)
            self.owner_payable = round(self.net_income * (flt(c.owner_share_percent) / 100.0), 2)
            self.company_share = round(self.net_income * (flt(c.company_share_percent) / 100.0), 2)
