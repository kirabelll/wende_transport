import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DriverRewardPenalty(Document):
    def on_update(self):
        if self.status == "Applied" and self.driver:
            existing = frappe.get_all("Driver Ledger Entry", filters={"reference_id": self.name})
            if not existing:
                last_entry = frappe.get_all("Driver Ledger Entry", filters={"driver": self.driver}, fields=["balance"], order_by="creation desc", limit=1)
                prev_balance = last_entry[0].balance if last_entry else 0.0
                amt = flt(self.amount)
                
                is_credit = self.type == "Reward"
                new_balance = prev_balance + amt if is_credit else prev_balance - amt
                category = "incentive" if is_credit else "fine"

                doc = frappe.get_doc({
                    "doctype": "Driver Ledger Entry",
                    "driver": self.driver,
                    "type": "Credit" if is_credit else "Debit",
                    "category": category,
                    "amount": amt,
                    "balance": new_balance,
                    "reference_type": "Driver Reward Penalty",
                    "reference_id": self.name,
                    "description": f"{self.type}: {self.reason or 'Performance score adjustment'} (ETB {amt:,.2f})"
                })
                doc.insert(ignore_permissions=True)
