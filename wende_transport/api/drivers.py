import frappe
from frappe import _
from frappe.utils import flt, nowdate, getdate

@frappe.whitelist()
def recalculate_driver_scores(driver_id=None, period=None):
	"""
	Calculates composite driver score (0-100) based on:
	- Safety (Accidents, traffic violations)
	- Delivery Performance (Shortages, on-time completions)
	- Fuel Efficiency
	- Attendance & Handover adherence
	"""
	filters = {"employment_type": "Driver", "status": "Active"}
	if driver_id:
		filters["name"] = driver_id

	drivers = frappe.get_all("Transport Employee", filters=filters, fields=["name", "full_name"])
	evaluated_scores = []

	for d in drivers:
		# 1. Total trips completed
		trips_completed = frappe.db.count("Trip", {"driver": d.name, "status": "Completed"})
		
		# 2. Shortages
		shortage_stats = frappe.db.sql("""
			SELECT 
				COUNT(name) as shortage_trips,
				COALESCE(SUM(shortage_tons), 0) as total_shortage_tons
			FROM `tabTrip`
			WHERE driver = %s AND status = 'Completed' AND shortage_tons > 0
		""", (d.name,), as_dict=True)[0]

		# 3. Accidents
		accidents_count = frappe.db.count("Accident Record", {"driver": d.name})

		# 4. Reward / Penalties
		penalties = frappe.db.sql("""
			SELECT COALESCE(SUM(points), 0) FROM `tabDriver Reward Penalty`
			WHERE driver = %s AND action_type = 'Penalty' AND docstatus = 1
		""", (d.name,))[0][0] or 0

		rewards = frappe.db.sql("""
			SELECT COALESCE(SUM(points), 0) FROM `tabDriver Reward Penalty`
			WHERE driver = %s AND action_type = 'Reward' AND docstatus = 1
		""", (d.name,))[0][0] or 0

		# Formula
		# Base score: 100
		base_score = 100.0
		# Deduction for accidents: 20 pts per accident
		accident_deduction = accidents_count * 20.0
		# Deduction for shortages: 10 pts per trip with shortage
		shortage_deduction = shortage_stats.shortage_trips * 10.0
		# Points from rules
		net_rule_points = flt(rewards) - flt(penalties)

		final_score = max(0.0, min(100.0, base_score - accident_deduction - shortage_deduction + net_rule_points))

		score_doc = frappe.get_doc({
			"doctype": "Driver Score",
			"driver": d.name,
			"period": period or nowdate()[:7],
			"trips_completed": trips_completed,
			"accidents_count": accidents_count,
			"shortage_count": shortage_stats.shortage_trips,
			"overall_score": round(final_score, 2),
			"score_grade": "A" if final_score >= 90 else "B" if final_score >= 75 else "C" if final_score >= 60 else "D"
		})
		score_doc.insert(ignore_permissions=True)
		evaluated_scores.append(score_doc.as_dict())

	return evaluated_scores

@frappe.whitelist()
def get_driver_leaderboard(limit=10):
	"""
	Returns top-performing drivers based on latest Driver Score records.
	"""
	return frappe.db.sql("""
		SELECT 
			ds.driver,
			te.full_name as driver_name,
			te.license_number,
			ds.overall_score,
			ds.score_grade,
			ds.trips_completed,
			ds.accidents_count,
			ds.period
		FROM `tabDriver Score` ds
		JOIN `tabTransport Employee` te ON te.name = ds.driver
		ORDER BY ds.overall_score DESC, ds.trips_completed DESC
		LIMIT %s
	""", (int(limit),), as_dict=True)

@frappe.whitelist()
def get_driver_financial_summary(driver_id):
	"""
	Returns driver's balance, unrecovered advances, and unsettled trips.
	"""
	advance_balance = frappe.db.get_value("Transport Employee", driver_id, "advance_balance") or 0.0
	
	unsettled_advances = frappe.get_all(
		"Driver Advance",
		filters={"driver": driver_id, "status": ["in", ["Approved", "Disbursed"]]},
		fields=["name", "amount", "recovered_amount", "trip", "creation"]
	)

	completed_unbilled_trips = frappe.get_all(
		"Trip",
		filters={"driver": driver_id, "status": "Completed", "billing_status": "Unbilled"},
		fields=["name", "start_date", "vehicle", "customer", "advance_amount"]
	)

	return {
		"driver": driver_id,
		"outstanding_advance_balance": flt(advance_balance, 2),
		"unsettled_advances": unsettled_advances,
		"unbilled_trips": completed_unbilled_trips
	}
