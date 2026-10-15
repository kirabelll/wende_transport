import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RentalVehicle(Document):
    def on_update(self):
        # Auto-mirror into Vehicle doctype for dispatching
        if not frappe.db.exists("Vehicle", self.plate_number):
            owner_doc = frappe.get_doc("Rental Owner", self.owner)
            veh = frappe.get_doc({
                "doctype": "Vehicle",
                "plate_number": self.plate_number,
                "vehicle_type": "Standalone",
                "make": f"Rental ({owner_doc.owner_name})",
                "model": self.vehicle_type or "Rental",
                "year": 2024,
                "capacity_tons": flt(self.capacity_tons),
                "ownership": "Rented",
                "owner_name": owner_doc.owner_name,
                "source_rental_vehicle": self.name,
                "status": "Active" if self.is_active else "Inactive",
                "operational_status": "Idle"
            })
            veh.insert(ignore_permissions=True)
