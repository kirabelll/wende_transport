import frappe

@frappe.whitelist()
def get_dispatch_board():
    """
    Returns active pipeline: pending orders, available trucks, and in-transit trips.
    """
    orders = frappe.get_all("Customer Order",
        filters={"status": ["in", ["Approved", "Scheduled"]]},
        fields=["name", "customer", "pickup_location", "delivery_location", "remaining_qty", "order_type", "order_date"]
    )
    available_trucks = frappe.get_all("Vehicle",
        filters={"status": "Active", "operational_status": "Idle", "compliance_locked": 0},
        fields=["name", "plate_number", "make", "model", "capacity_tons", "assigned_driver"]
    )
    in_transit_trips = frappe.get_all("Trip",
        filters={"status": ["in", ["Dispatched", "Loading", "In Transit", "Delivering"]]},
        fields=["name", "vehicle", "driver", "pickup_location", "delivery_location", "status", "planned_quantity_tons", "loaded_quantity_tons"]
    )

    return {
        "pending_orders": orders,
        "available_trucks": available_trucks,
        "active_trips": in_transit_trips
    }
