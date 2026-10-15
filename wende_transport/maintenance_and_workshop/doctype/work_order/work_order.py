import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds, flt, now_datetime

class WorkOrder(Document):
    def validate(self):
        labor = flt(self.labor_cost)
        parts = flt(self.parts_cost)
        self.total_cost = labor + parts

        if self.start_time and self.end_time:
            diff_secs = time_diff_in_seconds(self.end_time, self.start_time)
            self.total_downtime_hours = round(diff_secs / 3600.0, 2) if diff_secs > 0 else 0.0

    def on_update(self):
        if self.vehicle:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if self.status in ["Open", "In Progress"]:
                if veh.status != "Maintenance":
                    veh.status = "Maintenance"
                    veh.operational_status = "Maintenance"
                    veh.save(ignore_permissions=True)
            elif self.status == "Completed":
                # Check if there are other pending work orders or breakdown reports
                other_wo = frappe.get_all("Work Order", filters={"vehicle": self.vehicle, "status": ["in", ["Open", "In Progress"]], "name": ["!=", self.name]})
                other_brk = frappe.get_all("Breakdown Report", filters={"vehicle": self.vehicle, "status": ["in", ["Pending", "Approved"]]})
                if not other_wo and not other_brk:
                    veh.status = "Active"
                    veh.operational_status = "Locked" if veh.compliance_locked else "Idle"
                    veh.save(ignore_permissions=True)

                # Resolve linked breakdown report if any
                if self.breakdown_report:
                    brk = frappe.get_doc("Breakdown Report", self.breakdown_report)
                    if brk.status != "Resolved":
                        brk.status = "Resolved"
                        brk.save(ignore_permissions=True)

                # Update garage metrics
                if self.garage:
                    gar = frappe.get_doc("Garage", self.garage)
                    gar.total_jobs_done = (gar.total_jobs_done or 0) + 1
                    gar.total_spent = (gar.total_spent or 0) + flt(self.total_cost)
                    gar.save(ignore_permissions=True)
