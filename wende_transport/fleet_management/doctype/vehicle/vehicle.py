import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, now_datetime

class Vehicle(Document):
    def validate(self):
        self.check_compliance_lock()

    def check_compliance_lock(self):
        today = getdate(nowdate())
        reasons = []

        if self.insurance_expiry and getdate(self.insurance_expiry) <= today:
            reasons.append("Insurance expired on " + str(self.insurance_expiry))
        if self.inspection_expiry and getdate(self.inspection_expiry) <= today:
            reasons.append("Inspection expired on " + str(self.inspection_expiry))
        if self.permit_expiry and getdate(self.permit_expiry) <= today:
            reasons.append("Permit expired on " + str(self.permit_expiry))
        if self.libre_expiry and getdate(self.libre_expiry) <= today:
            reasons.append("Libre expired on " + str(self.libre_expiry))
        if self.bolo_expiry and getdate(self.bolo_expiry) <= today:
            reasons.append("Bolo expired on " + str(self.bolo_expiry))
        if self.road_fund_expiry and getdate(self.road_fund_expiry) <= today:
            reasons.append("Road Fund expired on " + str(self.road_fund_expiry))
        if self.roadworthiness_expiry and getdate(self.roadworthiness_expiry) <= today:
            reasons.append("Roadworthiness expired on " + str(self.roadworthiness_expiry))

        if reasons:
            self.compliance_locked = 1
            self.lock_reason = "; ".join(reasons)
            if not self.locked_at:
                self.locked_at = now_datetime()
            self.operational_status = "Locked"
        else:
            if self.compliance_locked and not self.get("__manual_lock"):
                self.compliance_locked = 0
                self.lock_reason = None
                self.locked_at = None
                if self.operational_status == "Locked":
                    self.operational_status = "Idle"

    @frappe.whitelist()
    def unlock_vehicle(self, reason="Manually cleared by Manager"):
        if not frappe.has_permission("Vehicle", "write"):
            frappe.throw("Not permitted to unlock vehicle")
        self.compliance_locked = 0
        self.lock_reason = None
        self.locked_at = None
        if self.operational_status == "Locked":
            self.operational_status = "Idle"
        self.save()
        frappe.msgprint(f"Vehicle {self.plate_number} has been unlocked.")
