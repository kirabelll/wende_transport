import frappe
from frappe import _

def after_install():
	"""
	Automatically seeds default roles, vehicle categories, maintenance templates,
	and standard operational rules when Wende Transport is installed.
	"""
	create_roles()
	seed_vehicle_categories()
	seed_maintenance_classes()
	seed_handover_checklist_items()
	seed_alert_rules()
	seed_approval_rules()

def create_roles():
	roles = [
		"Fleet Manager",
		"Dispatcher",
		"Technical Manager",
		"Operations Manager",
		"Safety Officer"
	]

	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1
			}).insert(ignore_permissions=True)

def seed_vehicle_categories():
	categories = [
		{"category_name": "Dry Bulk & High-Cube", "fuel_efficiency_standard": 2.2, "description": "Long-distance freight tractors with dry cargo trailers"},
		{"category_name": "Flatbed Container Carrier", "fuel_efficiency_standard": 2.4, "description": "Standard 20ft/40ft maritime container transporters"},
		{"category_name": "Fuel Tanker", "fuel_efficiency_standard": 2.1, "description": "Petroleum and bulk liquid tankers"},
		{"category_name": "Lowbed Heavy Haulage", "fuel_efficiency_standard": 1.8, "description": "Abnormal cargo and heavy construction equipment carriers"},
		{"category_name": "Tipper / Dump Truck", "fuel_efficiency_standard": 2.6, "description": "Aggregate and mining aggregate haulers"}
	]
	for c in categories:
		if not frappe.db.exists("Vehicle Category", c["category_name"]):
			frappe.get_doc({
				"doctype": "Vehicle Category",
				**c
			}).insert(ignore_permissions=True)

def seed_maintenance_classes():
	classes = [
		{"class_name": "A-Service", "interval_km": 5000, "estimated_labor_hours": 3, "description": "Engine oil replacement, oil filter, primary fuel filter, multi-point visual check"},
		{"class_name": "B-Service", "interval_km": 15000, "estimated_labor_hours": 6, "description": "A-Service + Air filter, secondary fuel filter, brake lining inspection, grease driveline"},
		{"class_name": "C-Service", "interval_km": 30000, "estimated_labor_hours": 12, "description": "Major overhaul, gearbox and differential oil flush, valve lash adjustment, cooling system flush"}
	]
	for m in classes:
		if not frappe.db.exists("Maintenance Class Template", m["class_name"]):
			frappe.get_doc({
				"doctype": "Maintenance Class Template",
				**m
			}).insert(ignore_permissions=True)

def seed_handover_checklist_items():
	items = [
		{"item_name": "Engine Oil & Coolant Levels", "category": "Mechanical", "mandatory": 1},
		{"item_name": "Tyre Condition & Pressures (All Axles)", "category": "Mechanical", "mandatory": 1},
		{"item_name": "Spare Tyre, Heavy-Duty Jack & Wheel Spanner", "category": "Safety Equipment", "mandatory": 1},
		{"item_name": "Fire Extinguisher & Warning Triangles", "category": "Safety Equipment", "mandatory": 1},
		{"item_name": "Cargo Tarpaulin, Straps & Belts", "category": "Logistics Gear", "mandatory": 1},
		{"item_name": "GPS Telematics Unit Operational", "category": "Electronics", "mandatory": 1},
		{"item_name": "Vehicle Registration & Insurance Documents in Cab", "category": "Documentation", "mandatory": 1}
	]
	for itm in items:
		if not frappe.db.exists("Handover Checklist Item", itm["item_name"]):
			frappe.get_doc({
				"doctype": "Handover Checklist Item",
				**itm
			}).insert(ignore_permissions=True)

def seed_alert_rules():
	rules = [
		{"rule_name": "Insurance Expiry Alert", "event_type": "Insurance Expiry", "days_before": 7, "severity": "High"},
		{"rule_name": "Inspection Certificate Expiry", "event_type": "Inspection Expiry", "days_before": 15, "severity": "High"},
		{"rule_name": "Driver License Expiry Warning", "event_type": "Driver License Expiry", "days_before": 15, "severity": "Medium"},
		{"rule_name": "Missing POD Delivery Follow-up", "event_type": "Missing POD", "days_before": 3, "severity": "High"}
	]
	for r in rules:
		if not frappe.db.exists("Alert Rule", r["rule_name"]):
			frappe.get_doc({
				"doctype": "Alert Rule",
				**r
			}).insert(ignore_permissions=True)

def seed_approval_rules():
	approvals = [
		{"rule_name": "Driver Advance Disbursal Approval", "doctype_target": "Driver Advance", "threshold_amount": 10000.0, "approver_role": "Fleet Manager"}
	]
	for a in approvals:
		if not frappe.db.exists("Approval Rule", a["rule_name"]):
			frappe.get_doc({
				"doctype": "Approval Rule",
				**a
			}).insert(ignore_permissions=True)

