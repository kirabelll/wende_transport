import frappe
from frappe.model.document import Document

class AccidentRecord(Document):
    def on_update(self):
        if self.vehicle and self.repair_status in ["Pending", "In Progress"]:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if veh.status != "Breakdown":
                veh.status = "Breakdown"
                veh.operational_status = "Maintenance"
                veh.save(ignore_permissions=True)
