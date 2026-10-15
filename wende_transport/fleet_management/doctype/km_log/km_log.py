import frappe
from frappe.model.document import Document

class KmLog(Document):
    def on_update(self):
        if self.vehicle and self.km_reading:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if (veh.current_km or 0) < self.km_reading:
                veh.current_km = self.km_reading
                veh.save(ignore_permissions=True)
