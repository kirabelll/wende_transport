import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate, now_datetime
from wende_transport.api.telegram import send_telegram_alert

@frappe.whitelist()
def evaluate_operations_alerts():
	"""
	Scans the entire operational system for bottlenecks, compliance violations,
	and low stock conditions. Generates Operations Alert entries and notifies via Telegram.
	"""
	today = getdate(nowdate())
	created_alerts = []

	def create_alert(alert_type, severity, title, message, ref_doctype=None, ref_docname=None):
		# Prevent duplicate open alerts for the same document and alert type
		existing = frappe.db.get_value("Operations Alert", {
			"alert_type": alert_type,
			"reference_doctype": ref_doctype,
			"reference_docname": ref_docname,
			"status": "Open"
		}, "name")
		
		if not existing:
			alert = frappe.get_doc({
				"doctype": "Operations Alert",
				"alert_type": alert_type,
				"severity": severity,
				"title": title,
				"message": message,
				"reference_doctype": ref_doctype,
				"reference_docname": ref_docname,
				"status": "Open"
			})
			alert.insert(ignore_permissions=True)
			created_alerts.append(alert.name)

			# Dispatch Telegram alert if high or critical severity
			if severity in ["High", "Critical"]:
				try:
					send_telegram_alert(f"🚨 *{severity.upper()} ALERT: {title}*\n{message}")
				except Exception:
					pass

	# 1. Vehicle Compliance Expiries
	vehicles = frappe.get_all(
		"Vehicle",
		filters={"status": ["!=", "Decommissioned"]},
		fields=["name", "license_plate", "insurance_expiry", "road_fund_expiry", "inspection_expiry"]
	)
	for v in vehicles:
		if v.insurance_expiry and getdate(v.insurance_expiry) < today:
			create_alert("Compliance", "Critical", f"Insurance Expired: {v.license_plate}",
				f"Insurance for vehicle {v.license_plate} expired on {v.insurance_expiry}.", "Vehicle", v.name)
		elif v.insurance_expiry and getdate(v.insurance_expiry) <= add_days(today, 7):
			create_alert("Compliance", "Medium", f"Insurance Due Soon: {v.license_plate}",
				f"Insurance for vehicle {v.license_plate} will expire on {v.insurance_expiry}.", "Vehicle", v.name)

		if v.inspection_expiry and getdate(v.inspection_expiry) < today:
			create_alert("Compliance", "High", f"Annual Inspection Expired: {v.license_plate}",
				f"Inspection for vehicle {v.license_plate} expired on {v.inspection_expiry}.", "Vehicle", v.name)

	# 2. Driver License Expiry
	drivers = frappe.get_all(
		"Transport Employee",
		filters={"employment_type": "Driver", "status": "Active"},
		fields=["name", "full_name", "license_expiry_date"]
	)
	for d in drivers:
		if d.license_expiry_date and getdate(d.license_expiry_date) < today:
			create_alert("Compliance", "Critical", f"Driver License Expired: {d.full_name}",
				f"Driver {d.full_name}'s license expired on {d.license_expiry_date}.", "Transport Employee", d.name)
		elif d.license_expiry_date and getdate(d.license_expiry_date) <= add_days(today, 15):
			create_alert("Compliance", "Medium", f"Driver License Expiring Soon: {d.full_name}",
				f"Driver {d.full_name}'s license will expire on {d.license_expiry_date}.", "Transport Employee", d.name)

	# 3. Missing POD on completed trips > 3 days
	completed_trips = frappe.db.sql("""
		SELECT name, vehicle, customer, end_date
		FROM `tabTrip`
		WHERE status = 'Completed' AND (pod_document IS NULL OR pod_document = '')
		  AND end_date <= %s
	""", (add_days(today, -3),), as_dict=True)

	for t in completed_trips:
		create_alert("Delayed POD", "High", f"Missing POD: Trip {t.name}",
			f"Trip {t.name} for customer {t.customer} was completed on {t.end_date} but POD is still missing.", "Trip", t.name)

	# 4. Overdue Work Orders
	overdue_wos = frappe.db.sql("""

		SELECT name, vehicle, expected_completion
		FROM `tabWork Order`
		WHERE status IN ('Open', 'In Progress') AND expected_completion < %s
	""", (today,), as_dict=True)

	for wo in overdue_wos:
		create_alert("Maintenance Overdue", "High", f"Overdue Work Order: {wo.name}",
			f"Work Order {wo.name} on vehicle {wo.vehicle} was expected to finish on {wo.expected_completion}.",
			"Work Order", wo.name)

	return {
		"alerts_evaluated_at": str(now_datetime()),
		"new_alerts_count": len(created_alerts),
		"alert_ids": created_alerts
	}
