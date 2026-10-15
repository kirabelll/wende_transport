import frappe
from frappe.utils import getdate, nowdate
from wende_transport.api.telegram import send_notification

def on_work_order_update(doc, method):
    pass

@frappe.whitelist()
def check_due_schedules():
    """
    Daily scheduled job to evaluate maintenance schedules and notify workshop managers.
    """
    schedules = frappe.get_all("Maintenance Schedule", filters={"status": ["!=", "Completed"]}, fields=["name", "vehicle", "maintenance_type", "next_due_date", "next_due_km"])
    overdue_count = 0
    due_soon_count = 0

    for s_row in schedules:
        sch = frappe.get_doc("Maintenance Schedule", s_row.name)
        old_status = sch.status
        sch.evaluate_schedule_status()
        if sch.status != old_status:
            sch.save(ignore_permissions=True)
            if sch.status == "Overdue":
                overdue_count += 1
                send_notification("urgent", "maintenance", f"Overdue Maintenance: {sch.vehicle}",
                    f"Vehicle {sch.vehicle} is OVERDUE for {sch.maintenance_type}.\nDue KM: {sch.next_due_km} | Due Date: {sch.next_due_date}")
            elif sch.status == "Due Soon":
                due_soon_count += 1

    return {"overdue": overdue_count, "due_soon": due_soon_count}

@frappe.whitelist()
def get_workshop_kpis():
    work_orders = frappe.get_all("Work Order", fields=["status", "total_cost", "total_downtime_hours"])
    breakdowns = frappe.get_all("Breakdown Report", fields=["status"])

    open_wo = sum(1 for w in work_orders if w.status in ["Open", "In Progress"])
    completed_wo = sum(1 for w in work_orders if w.status == "Completed")
    total_spend = sum(w.total_cost for w in work_orders if w.total_cost)
    total_downtime = sum(w.total_downtime_hours for w in work_orders if w.total_downtime_hours)
    pending_breakdowns = sum(1 for b in breakdowns if b.status in ["Pending", "Approved"])

    return {
        "open_work_orders": open_wo,
        "completed_work_orders": completed_wo,
        "total_repair_spend": total_spend,
        "total_downtime_hours": total_downtime,
        "pending_breakdowns": pending_breakdowns
    }
