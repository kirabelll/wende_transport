frappe.ui.form.on("Trip", {
    refresh(frm) {
        // Lifecycle actions
        if (frm.doc.status === "Planned") {
            frm.add_custom_button(__("Dispatch"), () => {
                frm.call("dispatch_trip").then(() => frm.reload_doc());
            }, __("Status Transition")).addClass("btn-primary");
        } else if (frm.doc.status === "Dispatched") {
            frm.add_custom_button(__("Start Loading"), () => {
                frm.call("start_loading").then(() => frm.reload_doc());
            }, __("Status Transition")).addClass("btn-info");
        } else if (frm.doc.status === "Loading") {
            frm.add_custom_button(__("Mark In Transit"), () => {
                frappe.prompt([
                    {
                        fieldname: "loaded_quantity",
                        fieldtype: "Float",
                        label: __("Loaded Tonnage (Tons)"),
                        default: frm.doc.loaded_quantity_tons || frm.doc.planned_quantity_tons,
                        reqd: 1
                    }
                ], (values) => {
                    frm.call("mark_in_transit", { loaded_quantity: values.loaded_quantity }).then(() => frm.reload_doc());
                }, __("Confirm Departure"), __("Start Transit"));
            }, __("Status Transition")).addClass("btn-warning");
        } else if (frm.doc.status === "In Transit" || frm.doc.status === "Delivering") {
            frm.add_custom_button(__("Close / Complete Trip"), () => {
                let loaded = frm.doc.loaded_quantity_tons || frm.doc.planned_quantity_tons || 0;
                frappe.prompt([
                    {
                        fieldname: "delivered_quantity",
                        fieldtype: "Float",
                        label: __("Delivered Quantity (Tons)"),
                        default: loaded,
                        reqd: 1
                    },
                    {
                        fieldname: "customer_deducted",
                        fieldtype: "Check",
                        label: __("Customer Deducted for Shortage?"),
                        default: 0
                    },
                    {
                        fieldname: "customer_deduction_amount",
                        fieldtype: "Currency",
                        label: __("Customer Deduction Amount (ETB)"),
                        depends_on: "eval:doc.customer_deducted==1"
                    },
                    {
                        fieldname: "driver_penalty_amount",
                        fieldtype: "Currency",
                        label: __("Driver Shortage Penalty (ETB)")
                    },
                    {
                        fieldname: "notes",
                        fieldtype: "Small Text",
                        label: __("Closing Remarks")
                    }
                ], (values) => {
                    frm.call("close_trip", values).then(() => frm.reload_doc());
                }, __("Trip Delivery Confirmation"), __("Confirm & Close"));
            }, __("Status Transition")).addClass("btn-success");
        }

        // Quick entry buttons for operational expenses
        if (frm.doc.status !== "Completed" && frm.doc.status !== "Cancelled") {
            frm.add_custom_button(__("Driver Advance"), () => {
                frappe.new_doc("Driver Advance", {
                    driver: frm.doc.driver,
                    trip: frm.doc.name,
                    amount: 2500
                });
            }, __("Operational Expenses"));

            frm.add_custom_button(__("Log Fuel"), () => {
                frappe.new_doc("Fuel Log", {
                    vehicle: frm.doc.vehicle,
                    driver: frm.doc.driver,
                    trip: frm.doc.name
                });
            }, __("Operational Expenses"));
        }

        if (frm.doc.status === "Completed") {
            frm.add_custom_button(__("Calculate Actual Costs"), () => {
                frappe.call({
                    method: "wende_transport.api.trips.calculate_trip_costs",
                    args: { trip_id: frm.doc.name },
                    callback(r) {
                        frm.reload_doc();
                    }
                });
            }, __("Analytics"));
        }
    },

    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle, ["assigned_driver", "compliance_locked", "lock_reason", "capacity_tons"], (r) => {
                if (r) {
                    if (r.compliance_locked) {
                        frappe.msgprint({
                            title: __("Compliance Alert"),
                            indicator: "red",
                            message: __("Selected vehicle is LOCKED: {0}", [r.lock_reason])
                        });
                    }
                    if (r.assigned_driver && !frm.doc.driver) {
                        frm.set_value("driver", r.assigned_driver);
                    }
                    if (r.capacity_tons && !frm.doc.planned_quantity_tons) {
                        frm.set_value("planned_quantity_tons", r.capacity_tons);
                    }
                }
            });
        }
    }
});
