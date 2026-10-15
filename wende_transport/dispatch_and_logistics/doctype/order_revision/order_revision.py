import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class OrderRevision(Document):
    def on_update(self):
        if self.status == "Approved" and self.order:
            order = frappe.get_doc("Customer Order", self.order)
            if self.field_changed in ["rate_per_ton", "adjusted_rate", "rate"]:
                order.adjusted_rate = float(self.new_value)
                order.save()
            elif self.field_changed == "quantity":
                order.quantity = float(self.new_value)
                order.save()
            elif hasattr(order, self.field_changed):
                setattr(order, self.field_changed, self.new_value)
                order.save()
