import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

@frappe.whitelist()
def check_contract_expiries():
	"""
	Scheduled / on-demand check for expiring and expired contracts:
	- Rate Contract
	- Revenue Share Contract
	- Rental Owner contracts
	"""
	today = getdate(nowdate())
	warning_date = add_days(today, 30)

	expired_count = 0
	warning_count = 0

	# 1. Rate Contracts
	active_rate_contracts = frappe.get_all(
		"Rate Contract",
		filters={"status": "Active"},
		fields=["name", "customer", "valid_to"]
	)
	for rc in active_rate_contracts:
		if not rc.valid_to:
			continue
		v_to = getdate(rc.valid_to)
		if v_to < today:
			frappe.db.set_value("Rate Contract", rc.name, "status", "Expired")
			expired_count += 1
		elif v_to <= warning_date:
			warning_count += 1

	# 2. Revenue Share Contracts
	rev_contracts = frappe.get_all(
		"Revenue Share Contract",
		filters={"status": "Active"},
		fields=["name", "partner_name", "end_date"]
	)
	for rsc in rev_contracts:
		if not rsc.end_date:
			continue
		e_date = getdate(rsc.end_date)
		if e_date < today:
			frappe.db.set_value("Revenue Share Contract", rsc.name, "status", "Expired")
			expired_count += 1
		elif e_date <= warning_date:
			warning_count += 1

	return {
		"today": str(today),
		"contracts_expired_marked": expired_count,
		"contracts_expiring_soon_count": warning_count
	}

@frappe.whitelist()
def get_expiring_contracts_list(days=30):
	"""
	Returns all contracts expiring within the specified number of days.
	"""
	today = getdate(nowdate())
	cutoff = add_days(today, int(days))

	results = []

	rate_contracts = frappe.get_all(
		"Rate Contract",
		filters={"status": "Active", "valid_to": ["between", [today, cutoff]]},
		fields=["name", "customer", "valid_to"]
	)
	for rc in rate_contracts:
		results.append({
			"doctype": "Rate Contract",
			"name": rc.name,
			"party": rc.customer,
			"expiry_date": str(rc.valid_to),
			"days_left": (getdate(rc.valid_to) - today).days
		})

	rev_contracts = frappe.get_all(
		"Revenue Share Contract",
		filters={"status": "Active", "end_date": ["between", [today, cutoff]]},
		fields=["name", "partner_name", "end_date"]
	)
	for rsc in rev_contracts:
		results.append({
			"doctype": "Revenue Share Contract",
			"name": rsc.name,
			"party": rsc.partner_name,
			"expiry_date": str(rsc.end_date),
			"days_left": (getdate(rsc.end_date) - today).days
		})

	return sorted(results, key=lambda x: x["days_left"])
