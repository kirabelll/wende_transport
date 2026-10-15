import frappe
from frappe.model.document import Document

class DriverAssignment(Document):
    def on_update(self):
        if self.status == "Active" and self.vehicle and self.driver:
            # Update assigned driver on vehicle
            vehicle_doc = frappe.get_doc("Vehicle", self.vehicle)
            if vehicle_doc.assigned_driver != self.driver:
                vehicle_doc.assigned_driver = self.driver
                vehicle_doc.save(ignore_permissions=True)
