import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FuelLog(Document):
    def validate(self):
        liters = flt(self.liters)
        cost_per_liter = flt(self.cost_per_liter)
        self.total_cost = liters * cost_per_liter

    def on_update(self):
        # Update vehicle odometer reading
        if self.vehicle and self.odometer_km:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if (veh.current_km or 0) < self.odometer_km:
                veh.current_km = self.odometer_km
                veh.save(ignore_permissions=True)

        # Update trip fuel total
        if self.trip:
            trip = frappe.get_doc("Trip", self.trip)
            fuel_entries = frappe.get_all("Fuel Log", filters={"trip": self.trip}, fields=["total_cost"])
            trip.fuel_cost = sum(f.total_cost for f in fuel_entries)
            trip.allocated_fuel_cost = trip.fuel_cost
            trip.save(ignore_permissions=True)
