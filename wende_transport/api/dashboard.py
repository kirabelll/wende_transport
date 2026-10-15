import frappe
from frappe import _
from frappe.utils import flt, nowdate, get_first_day, get_last_day

@frappe.whitelist()
def get_executive_kpis():
	"""
	Returns consolidated executive KPIs for the Wende Transport operations desk dashboard.
	"""
	today = nowdate()
	first_day_month = get_first_day(today)

	# 1. Fleet Overview
	fleet_counts = frappe.db.sql("""
		SELECT 
			status,
			COUNT(name) as count
		FROM `tabVehicle`
		WHERE status != 'Decommissioned'
		GROUP BY status
	""", as_dict=True)

	fleet_summary = {"Available": 0, "On Trip": 0, "Maintenance": 0, "Breakdown": 0, "Total": 0}
	for row in fleet_counts:
		fleet_summary[row.status] = row.count
		fleet_summary["Total"] += row.count

	# 2. Logistics & Trips (Current Month)
	trip_stats = frappe.db.sql("""
		SELECT 
			COUNT(name) as total_trips,
			COALESCE(SUM(cargo_weight), 0) as total_tons,
			COALESCE(SUM(total_revenue), 0) as gross_revenue,
			COALESCE(SUM(total_cost), 0) as gross_cost,
			COALESCE(SUM(shortage_tons), 0) as total_shortage_tons
		FROM `tabTrip`
		WHERE creation >= %s
	""", (first_day_month,), as_dict=True)[0]

	active_trips_count = frappe.db.count("Trip", {"status": ["in", ["Dispatched", "Loading", "In Transit", "Delivered / Offloading"]]})

	# 3. Workshop
	open_work_orders = frappe.db.count("Work Order", {"status": ["in", ["Open", "In Progress", "Waiting for Parts"]]})

	# 4. Safety & Alerts
	open_alerts = frappe.db.count("Operations Alert", {"status": "Open"})
	critical_alerts = frappe.db.count("Operations Alert", {"status": "Open", "severity": "Critical"})
	accidents_this_month = frappe.db.count("Accident Record", {"accident_date": [">=", first_day_month]})

	return {
		"fleet": fleet_summary,
		"logistics": {
			"active_trips": active_trips_count,
			"month_trips": trip_stats.total_trips,
			"month_tons_moved": flt(trip_stats.total_tons, 2),
			"month_gross_revenue": flt(trip_stats.gross_revenue, 2),
			"month_gross_cost": flt(trip_stats.gross_cost, 2),
			"month_estimated_profit": flt(flt(trip_stats.gross_revenue) - flt(trip_stats.gross_cost), 2),
			"month_shortage_tons": flt(trip_stats.total_shortage_tons, 2)
		},
		"workshop": {
			"open_work_orders": open_work_orders
		},
		"safety_and_alerts": {
			"open_alerts": open_alerts,
			"critical_alerts": critical_alerts,
			"accidents_this_month": accidents_this_month
		}
	}

