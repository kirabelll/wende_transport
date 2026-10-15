import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, flt

class MaintenanceSchedule(Document):
    def validate(self):
        self.evaluate_schedule_status()

    def evaluate_schedule_status(self):
        today = getdate(nowdate())
        current_km = 0
        if self.vehicle:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            current_km = flt(veh.current_km)

        # KM check
        is_overdue = False
        is_due_soon = False

        if self.next_due_km:
            if current_km >= self.next_due_km:
                is_overdue = True
            elif current_km >= (self.next_due_km - (self.alert_before_km or 500)):
                is_due_soon = True

        # Date check
        if self.next_due_date:
            due_date = getdate(self.next_due_date)
            if today >= due_date:
                is_overdue = True
            elif (due_date - today).days <= (self.alert_before_days or 7):
                is_due_soon = True

        if is_overdue:
            self.status = "Overdue"
        elif is_due_soon:
            self.status = "Due Soon"
        else:
            if self.status not in ["Completed"]:
                self.status = "Upcoming"
