import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DriverScore(Document):
    def validate(self):
        # Weights: 20% trips, 25% shortage, 20% cycle time, 15% fuel, 10% attendance, 10% safety
        w_trip = flt(self.trip_score) * 0.20
        w_shortage = flt(self.shortage_score) * 0.25
        w_cycle = flt(self.cycle_time_score) * 0.20
        w_fuel = flt(self.fuel_score) * 0.15
        w_att = flt(self.attendance_score) * 0.10
        w_safety = flt(self.safety_score) * 0.10
        self.total_score = round(w_trip + w_shortage + w_cycle + w_fuel + w_att + w_safety, 2)
