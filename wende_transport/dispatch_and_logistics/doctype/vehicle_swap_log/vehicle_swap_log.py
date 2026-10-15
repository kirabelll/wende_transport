import frappe
from frappe.model.document import Document

class VehicleSwapLog(Document):
    def on_update(self):
        if self.trip and self.to_vehicle:
            trip = frappe.get_doc("Trip", self.trip)
            trip.vehicle = self.to_vehicle
            trip.save(ignore_permissions=True)
