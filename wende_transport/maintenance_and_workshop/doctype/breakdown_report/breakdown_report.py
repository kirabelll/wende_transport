import frappe
from frappe.model.document import Document

class BreakdownReport(Document):
    def on_update(self):
        if self.vehicle:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if self.status in ["Pending", "Approved"]:
                if veh.status != "Breakdown":
                    veh.status = "Breakdown"
                    veh.operational_status = "Maintenance"
                    veh.save(ignore_permissions=True)
            elif self.status == "Resolved":
                if veh.status == "Breakdown":
                    veh.status = "Active"
                    veh.operational_status = "Idle"
                    veh.save(ignore_permissions=True)
