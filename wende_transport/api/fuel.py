import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_fuel_variance_report(from_date=None, to_date=None):
    filters = {}
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]

    fuel_logs = frappe.get_all("Fuel Log", filters=filters, fields=["name", "vehicle", "trip", "driver", "date", "liters", "total_cost", "odometer_km"])
    standards = {s.route: s for s in frappe.get_all("Fuel Standard", filters={"is_active": 1}, fields=["route", "standard_liters", "standard_km_per_liter"])}

    variance_list = []
    for f in fuel_logs:
        route_name = None
        if f.trip:
            t = frappe.get_doc("Trip", f.trip)
            route_name = f"{t.pickup_location} → {t.delivery_location}"

        std = standards.get(route_name) if route_name else None
        target_liters = flt(std.standard_liters) if std else None
        variance_liters = (flt(f.liters) - target_liters) if target_liters else None

        variance_list.append({
            "fuel_log": f.name,
            "vehicle": f.vehicle,
            "trip": f.trip,
            "driver": f.driver,
            "date": f.date,
            "actual_liters": f.liters,
            "target_liters": target_liters,
            "variance_liters": round(variance_liters, 2) if variance_liters is not None else 0,
            "variance_status": "Over-consumption" if (variance_liters and variance_liters > 0) else "Normal",
            "total_cost": f.total_cost
        })

    return variance_list
