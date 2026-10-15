import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt

class DriverAdvance(Document):
    def on_update(self):
        if self.status == "Paid":
            if not self.paid_at:
                self.paid_at = now_datetime()

            # 1. Update trip advance total
            if self.trip:
                trip = frappe.get_doc("Trip", self.trip)
                advances = frappe.get_all("Driver Advance", filters={"trip": self.trip, "status": "Paid"}, fields=["amount"])
                trip.driver_advance_given = sum(a.amount for a in advances)
                trip.save(ignore_permissions=True)

            # 2. Record ledger entry
            existing = frappe.get_all("Driver Ledger Entry", filters={"reference_id": self.name, "category": "advance"})
            if not existing and self.driver:
                last_entry = frappe.get_all("Driver Ledger Entry", filters={"driver": self.driver}, fields=["balance"], order_by="creation desc", limit=1)
                prev_balance = last_entry[0].balance if last_entry else 0.0
                amt = flt(self.amount)
                new_balance = prev_balance - amt

                doc = frappe.get_doc({
                    "doctype": "Driver Ledger Entry",
                    "driver": self.driver,
                    "type": "Debit",
                    "category": "advance",
                    "amount": amt,
                    "balance": new_balance,
                    "reference_type": "Driver Advance",
                    "reference_id": self.name,
                    "description": f"Driver advance disburse for {self.reason or 'trip'} (ETB {amt:,.2f})"
                })
                doc.insert(ignore_permissions=True)
