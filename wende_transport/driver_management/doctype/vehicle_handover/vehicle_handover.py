import frappe
from frappe.model.document import Document

class VehicleHandover(Document):
    def on_update(self):
        if self.status == "Accepted" and self.vehicle and self.to_driver:
            # Reassign vehicle to incoming driver
            veh = frappe.get_doc("Vehicle", self.vehicle)
            prev_driver = veh.assigned_driver
            veh.assigned_driver = self.to_driver
            if self.km_reading and (veh.current_km or 0) < self.km_reading:
                veh.current_km = self.km_reading
            veh.save(ignore_permissions=True)

            # Create Driver Assignment record
            asgn = frappe.get_doc({
                "doctype": "Driver Assignment",
                "driver": self.to_driver,
                "vehicle": self.vehicle,
                "previous_plate": prev_driver,
                "reason": f"Vehicle Handover {self.name}",
                "status": "Active"
            })
            asgn.insert(ignore_permissions=True)
