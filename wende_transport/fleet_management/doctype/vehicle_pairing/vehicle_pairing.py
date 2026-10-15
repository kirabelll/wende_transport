import frappe
from frappe.model.document import Document

class VehiclePairing(Document):
    def validate(self):
        if self.front_vehicle == self.back_vehicle:
            frappe.throw("Front vehicle and back trailer cannot be the same vehicle.")
