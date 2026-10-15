import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import json

class ApprovalRequest(Document):
    @frappe.whitelist()
    def approve(self):
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_at = now_datetime()
        self.apply_approval_action()
        self.save()

    @frappe.whitelist()
    def reject(self, reason):
        self.status = "Rejected"
        self.rejected_by = frappe.session.user
        self.rejected_at = now_datetime()
        self.rejection_reason = reason
        self.save()

    def apply_approval_action(self):
        if self.request_type == "compliance_unlock" and self.entity_type == "Vehicle":
            veh = frappe.get_doc("Vehicle", self.entity_id)
            veh.compliance_locked = 0
            veh.lock_reason = "Manually approved override"
            veh.operational_status = "Idle"
            veh.save(ignore_permissions=True)
        elif self.request_type == "penalty_waiver" and self.entity_type == "Order Penalty":
            pen = frappe.get_doc("Order Penalty", self.entity_id)
            pen.status = "Waived"
            pen.waived_by = frappe.session.user
            pen.waived_reason = self.description
            pen.save(ignore_permissions=True)
