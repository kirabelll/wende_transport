app_name = "wende_transport"
app_title = "Wende Transport"
app_publisher = "Wende Transport Team"
app_description = "Enterprise Fleet, Logistics, Maintenance, Store, Fuel, Cashier and Operations Management for Frappe v15"
app_email = "info@wendetransport.com"
app_license = "mit"
required_apps = ["frappe"]

# Includes in <head>
# ------------------
# include js, css files in header of desk.html
app_include_css = "/assets/wende_transport/css/wende_transport.css"
app_include_js = "/assets/wende_transport/js/wende_transport.js"

# Installation & Migrations
# -------------------------
after_install = "wende_transport.setup.after_install"


# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "Trip": {
        "validate": "wende_transport.api.trips.validate_trip",
        "on_update": "wende_transport.api.trips.on_trip_update",
    },
    "Vehicle": {
        "validate": "wende_transport.api.vehicles.validate_vehicle",
        "on_update": "wende_transport.api.vehicles.on_vehicle_update",
    },
    "Customer Order": {
        "validate": "wende_transport.api.orders.validate_customer_order",
    },
    "Work Order": {
        "on_update": "wende_transport.api.maintenance.on_work_order_update",
    }
}


# Scheduled Tasks
# ---------------
scheduler_events = {
    "hourly": [
        "wende_transport.api.vehicles.check_compliance_expiry_all",
        "wende_transport.api.alerts.evaluate_operations_alerts",
    ],
    "daily": [
        "wende_transport.api.maintenance.check_due_schedules",
        "wende_transport.api.contracts.check_contract_expiries",
        "wende_transport.api.drivers.recalculate_driver_scores",
    ],
}

# Permissions & Fixtures
# ----------------------
fixtures = [
    {
        "doctype": "Role",
        "filters": [["role_name", "in", [
            "Fleet Manager",
            "Dispatcher",
            "Technical Manager",
            "Operations Manager",
            "Driver"
        ]]]

    },
    {
        "doctype": "Vehicle Category",
    },
    {
        "doctype": "Maintenance Class Template",
    },
    {
        "doctype": "Alert Rule",
    },
    {
        "doctype": "Approval Rule",
    }
]
