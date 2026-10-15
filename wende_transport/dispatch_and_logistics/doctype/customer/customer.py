import frappe
from frappe.model.document import Document

class Customer(Document):
    def validate(self):
        if self.credit_limit and self.outstanding_balance:
            if self.outstanding_balance > self.credit_limit:
                if not self.dispatch_blocked:
                    self.dispatch_blocked = 1
                    self.block_reason = f"Credit limit exceeded: ETB {self.outstanding_balance:,.2f} > limit ETB {self.credit_limit:,.2f}"
            elif self.outstanding_balance <= self.credit_limit and self.dispatch_blocked and "Credit limit exceeded" in (self.block_reason or ""):
                self.dispatch_blocked = 0
                self.block_reason = None
