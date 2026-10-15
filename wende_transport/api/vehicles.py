import frappe
from frappe.utils import getdate, nowdate, now_datetime, flt
from wende_transport.api.telegram import send_notification

def validate_vehicle(doc, method):
    doc.check_compliance_lock()

def on_vehicle_update(doc, method):
    pass

@frappe.whitelist()
def get_fleet_board():
    """
    Returns full fleet board with active trip, current work order, and operational summary.
    """
    vehicles = frappe.get_all("Vehicle",
        filters={"status": ["!=", "Inactive"]},
        fields=[
            "name", "plate_number", "make", "model", "category", "capacity_tons",
            "current_km", "status", "operational_status", "compliance_locked",
            "lock_reason", "assigned_driver", "ownership", "owner_name",
            "insurance_expiry", "inspection_expiry", "permit_expiry",
            "last_known_location", "last_location_at"
        ],
        order_by="plate_number asc"
    )

    board = []
    for v in vehicles:
        # Get active trip if any
        active_trip = frappe.get_all("Trip",
            filters={"vehicle": v.name, "status": ["in", ["Dispatched", "Loading", "In Transit", "Delivering"]]},
            fields=["name", "pickup_location", "delivery_location", "status", "order"],
            limit=1
        )
        # Get active work order if any
        active_wo = frappe.get_all("Work Order",
            filters={"vehicle": v.name, "status": ["in", ["Open", "In Progress"]]},
            fields=["name", "type", "description", "status"],
            limit=1
        )

        board.append({
            "vehicle": v,
            "current_trip": active_trip[0] if active_trip else None,
            "current_work_order": active_wo[0] if active_wo else None
        })

    summary = {
        "total": len(board),
        "idle": sum(1 for b in board if b["vehicle"]["operational_status"] == "Idle"),
        "on_trip": sum(1 for b in board if b["vehicle"]["operational_status"] == "On Trip"),
        "loading": sum(1 for b in board if b["vehicle"]["operational_status"] == "Loading"),
        "maintenance": sum(1 for b in board if b["vehicle"]["operational_status"] == "Maintenance"),
        "locked": sum(1 for b in board if b["vehicle"]["compliance_locked"])
    }

    return {"board": board, "summary": summary}

@frappe.whitelist()
def check_compliance_expiry_all():
    """
    Checks all vehicles for expired documents. Locks non-compliant vehicles automatically.
    """
    today = getdate(nowdate())
    vehicles = frappe.get_all("Vehicle", filters={"status": ["!=", "Inactive"]}, fields=["name", "plate_number"])
    locked_count = 0
    unlocked_count = 0

    for v_row in vehicles:
        veh = frappe.get_doc("Vehicle", v_row.name)
        was_locked = veh.compliance_locked
        veh.check_compliance_lock()
        if veh.compliance_locked != was_locked:
            veh.save(ignore_permissions=True)
            if veh.compliance_locked:
                locked_count += 1
                send_notification("urgent", "compliance", f"Compliance Lock: {veh.plate_number}",
                    f"Vehicle {veh.plate_number} has been locked.\nReason: {veh.lock_reason}")
            else:
                unlocked_count += 1

    return {"locked": locked_count, "unlocked": unlocked_count}

@frappe.whitelist()
def get_depreciation_overview():
    vehicles = frappe.get_all("Vehicle",
        filters={"status": ["!=", "Inactive"], "purchase_cost": [">", 0]},
        fields=["name", "plate_number", "purchase_cost", "residual_value", "useful_life_years", "year"]
    )
    result = []
    for v in vehicles:
        cost = flt(v.purchase_cost)
        residual = flt(v.residual_value)
        years = flt(v.useful_life_years) or 5.0
        annual = (cost - residual) / years
        monthly = annual / 12.0
        result.append({
            "plate_number": v.plate_number,
            "purchase_cost": cost,
            "residual_value": residual,
            "useful_life_years": years,
            "annual_depreciation": round(annual, 2),
            "monthly_depreciation": round(monthly, 2)
        })
    return result
