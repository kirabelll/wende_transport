import frappe
from frappe.utils import flt, now_datetime, getdate, time_diff_in_seconds
from wende_transport.api.telegram import send_notification

def validate_trip(doc, method):
    doc.enforce_vehicle_compliance()
    doc.enforce_customer_credit()
    doc.calculate_shortage_and_revenue()
    doc.calculate_cycle_time()

def on_trip_update(doc, method):
    # Telegram alerts on creation or completion
    if doc.get("__islocal"):
        send_notification("info", "trip", f"New Trip Created: {doc.name}",
            f"Vehicle: {doc.vehicle}\nDriver: {doc.driver}\nRoute: {doc.pickup_location} → {doc.delivery_location}\nPlanned Tonnage: {doc.planned_quantity_tons} tons")
    elif doc.status == "Completed":
        if flt(doc.shortage) > 0:
            send_notification("urgent", "trip", f"Trip Completed with SHORTAGE: {doc.name}",
                f"Vehicle: {doc.vehicle}\nDelivered: {doc.delivered_quantity_tons} tons | Shortage: {doc.shortage} tons\nDeduction: ETB {doc.shortage_deduction:,.2f}")
        else:
            send_notification("info", "trip", f"Trip Completed: {doc.name}",
                f"Vehicle: {doc.vehicle}\nDelivered: {doc.delivered_quantity_tons} tons | Revenue: ETB {doc.revenue:,.2f}")

@frappe.whitelist()
def get_trip_kpis(from_date=None, to_date=None):
    filters = {"docstatus": ["!=", 2]}
    if from_date and to_date:
        filters["trip_date"] = ["between", [from_date, to_date]]

    trips = frappe.get_all("Trip", filters=filters, fields=["status", "delivered_quantity_tons", "revenue", "total_cycle_minutes"])
    completed = [t for t in trips if t.status == "Completed"]

    total_tonnage = sum(flt(t.delivered_quantity_tons) for t in completed)
    total_revenue = sum(flt(t.revenue) for t in completed)
    valid_cycles = [t.total_cycle_minutes for t in completed if t.total_cycle_minutes]
    avg_cycle = round(sum(valid_cycles) / len(valid_cycles), 1) if valid_cycles else 0

    return {
        "total_trips": len(trips),
        "completed_trips": len(completed),
        "total_tonnage": total_tonnage,
        "total_revenue": total_revenue,
        "avg_cycle_minutes": avg_cycle
    }

@frappe.whitelist()
def suggest_assignment(planned_quantity_tons=0, pickup_location=None, delivery_location=None):
    """
    Intelligent dispatch suggestion algorithm:
    Scores active vehicles and drivers based on capacity fit, route familiarity, workload balance, and fuel efficiency.
    """
    planned_qty = flt(planned_quantity_tons)
    busy_trips = frappe.get_all("Trip", filters={"status": ["in", ["Dispatched", "Loading", "In Transit", "Delivering"]]}, fields=["vehicle", "driver"])
    busy_vehicles = set(t.vehicle for t in busy_trips if t.vehicle)
    busy_drivers = set(t.driver for t in busy_trips if t.driver)

    # 1. Available Vehicles
    veh_filters = {"status": "Active", "compliance_locked": 0}
    all_vehicles = frappe.get_all("Vehicle", filters=veh_filters, fields=["name", "plate_number", "make", "model", "category", "capacity_tons", "assigned_driver"])
    available_vehicles = [v for v in all_vehicles if v.name not in busy_vehicles]

    scored_vehicles = []
    for v in available_vehicles:
        score = 50.0
        cap = flt(v.capacity_tons)
        if planned_qty > 0:
            if cap >= planned_qty:
                score += 20.0
            else:
                score -= 30.0

        if pickup_location or delivery_location:
            route_filters = {"vehicle": v.name, "status": "Completed"}
            if delivery_location:
                route_filters["delivery_location"] = ["like", f"%{delivery_location}%"]
            route_count = frappe.db.count("Trip", route_filters)
            score += min(route_count * 5.0, 20.0)

        scored_vehicles.append({
            "name": v.name,
            "plate_number": v.plate_number,
            "make": v.make,
            "model": v.model,
            "capacity_tons": v.capacity_tons,
            "assigned_driver": v.assigned_driver,
            "score": min(100.0, max(0.0, score))
        })
    scored_vehicles.sort(key=lambda x: x["score"], reverse=True)

    # 2. Available Drivers
    all_drivers = frappe.get_all("Transport Employee", filters={"role": "Driver", "status": "Active"}, fields=["name", "full_name", "emp_number", "phone"])
    available_drivers = [d for d in all_drivers if d.name not in busy_drivers]

    scored_drivers = []
    for d in available_drivers:
        score = 50.0
        if delivery_location:
            route_exp = frappe.db.count("Trip", {"driver": d.name, "status": "Completed", "delivery_location": ["like", f"%{delivery_location}%"]})
            score += min(route_exp * 5.0, 25.0)

        # Workload balance (fewer active trips in last 7 days = higher priority)
        weekly_trips = frappe.db.count("Trip", {"driver": d.name, "creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -7)]})
        score += max(0.0, 20.0 - (weekly_trips * 4.0))

        scored_drivers.append({
            "name": d.name,
            "full_name": d.full_name,
            "emp_number": d.emp_number,
            "phone": d.phone,
            "score": min(100.0, max(0.0, score))
        })
    scored_drivers.sort(key=lambda x: x["score"], reverse=True)

    return {
        "vehicles": scored_vehicles[:5],
        "drivers": scored_drivers[:5]
    }

@frappe.whitelist()
def get_time_analytics(vehicle=None, driver=None, from_date=None, to_date=None):
    filters = {"status": "Completed"}
    if vehicle:
        filters["vehicle"] = vehicle
    if driver:
        filters["driver"] = driver
    if from_date and to_date:
        filters["trip_date"] = ["between", [from_date, to_date]]

    trips = frappe.get_all("Trip", filters=filters, fields=[
        "name", "pickup_location", "delivery_location", "vehicle", "driver",
        "loading_start_time", "loading_end_time", "departure_time", "arrival_at_delivery",
        "unloading_start_time", "unloading_end_time", "total_cycle_minutes"
    ])

    results = []
    for t in trips:
        loading_min = int(time_diff_in_seconds(t.loading_end_time, t.loading_start_time) / 60) if (t.loading_end_time and t.loading_start_time) else 0
        travel_min = int(time_diff_in_seconds(t.arrival_at_delivery, t.departure_time) / 60) if (t.arrival_at_delivery and t.departure_time) else 0
        unloading_min = int(time_diff_in_seconds(t.unloading_end_time, t.unloading_start_time) / 60) if (t.unloading_end_time and t.unloading_start_time) else 0
        total_min = t.total_cycle_minutes or (loading_min + travel_min + unloading_min)
        wait_min = max(0, total_min - loading_min - travel_min - unloading_min)

        results.append({
            "trip": t.name,
            "route": f"{t.pickup_location} → {t.delivery_location}",
            "vehicle": t.vehicle,
            "driver": t.driver,
            "loading_min": loading_min,
            "travel_min": travel_min,
            "unloading_min": unloading_min,
            "wait_min": wait_min,
            "total_min": total_min
        })

    return results

@frappe.whitelist()
def calculate_trip_costs(trip_id):
    trip = frappe.get_doc("Trip", trip_id)
    # 1. Fuel cost from fuel logs
    fuel_logs = frappe.get_all("Fuel Log", filters={"trip": trip_id}, fields=["total_cost"])
    trip.allocated_fuel_cost = sum(flt(f.total_cost) for f in fuel_logs)

    # 2. Driver daily rate
    if trip.driver:
        drv = frappe.get_doc("Transport Employee", trip.driver)
        basic = flt(drv.basic_salary)
        trip.allocated_driver_cost = round(basic / 26.0, 2) if basic > 0 else 0.0

    # 3. Prorated maintenance
    if trip.vehicle:
        recent_orders = frappe.get_all("Work Order", filters={"vehicle": trip.vehicle, "status": "Completed"}, fields=["total_cost"], limit=10)
        avg_maint = sum(flt(w.total_cost) for w in recent_orders) / len(recent_orders) if recent_orders else 0.0
        trip.allocated_maintenance_cost = round(avg_maint / 4.0, 2)

    # 4. Depreciation daily prorated
    if trip.vehicle:
        veh = frappe.get_doc("Vehicle", trip.vehicle)
        if flt(veh.purchase_cost) > 0 and flt(veh.useful_life_years) > 0:
            annual_depr = (flt(veh.purchase_cost) - flt(veh.residual_value)) / flt(veh.useful_life_years)
            trip.allocated_depreciation_cost = round(annual_depr / 300.0, 2)

    trip.calculate_profitability()
    trip.save()
    return trip.total_trip_cost
