import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RevenueShareTrip(Document):
    def validate(self):
        exp = [
            self.fuel_cost, self.driver_per_diem, self.gps_cost,
            self.insurance_cost, self.broker_commission, self.other_expenses
        ]
        self.total_expenses = sum(flt(x) for x in exp)
        rev = flt(self.trip_revenue)
        self.net_income = rev - self.total_expenses

        if self.contract:
            c = frappe.get_doc("Revenue Share Contract", self.contract)
            owner_pct = flt(c.owner_share_percent) / 100.0
            comp_pct = flt(c.company_share_percent) / 100.0
            self.owner_share = round(self.net_income * owner_pct, 2)
            self.company_share = round(self.net_income * comp_pct, 2)
