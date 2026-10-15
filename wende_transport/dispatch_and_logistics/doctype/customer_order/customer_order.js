frappe.ui.form.on("Customer Order", {
    refresh(frm) {
        if (frm.doc.status === "Approved" || frm.doc.status === "Scheduled") {
            frm.add_custom_button(__("Dispatch Trip"), () => {
                frappe.new_doc("Trip", {
                    order: frm.doc.name,
                    customer: frm.doc.customer,
                    order_type: frm.doc.order_type,
                    pickup_location: frm.doc.pickup_location,
                    delivery_location: frm.doc.delivery_location,
                    rate_per_ton: frm.doc.adjusted_rate || frm.doc.base_rate,
                    planned_quantity_tons: frm.doc.remaining_qty || frm.doc.quantity
                });
            }, __("Dispatch"));
        }

        if (frm.doc.total_delivered > 0 && frm.doc.status !== "Invoiced") {
            frm.add_custom_button(__("Generate Settlement"), () => {
                frappe.call({
                    method: "wende_transport.api.settlements.generate_order_settlement",
                    args: { order_id: frm.doc.name },
                    callback(r) {
                        if (r.message) {
                            frappe.set_route("Form", "Trip Settlement", r.message);
                        }
                    }
                });
            }, __("Billing"));
        }

        frm.add_custom_button(__("View Linked Trips"), () => {
            frappe.set_route("List", "Trip", { order: frm.doc.name });
        }, __("History"));
    },

    customer(frm) {
        if (frm.doc.customer) {
            frappe.db.get_value("Customer", frm.doc.customer, ["dispatch_blocked", "block_reason"], (r) => {
                if (r && r.dispatch_blocked) {
                    frappe.msgprint({
                        title: __("Credit Warning"),
                        indicator: "red",
                        message: __("Customer is currently blocked: {0}", [r.block_reason])
                    });
                }
            });
        }
    },

    quantity(frm) {
        frm.trigger("calculate_total");
    },
    base_rate(frm) {
        frm.trigger("calculate_total");
    },
    adjusted_rate(frm) {
        frm.trigger("calculate_total");
    },
    calculate_total(frm) {
        let rate = frm.doc.adjusted_rate || frm.doc.base_rate || 0;
        let qty = frm.doc.quantity || 0;
        frm.set_value("total_amount", qty * rate);
        frm.set_value("remaining_qty", Math.max(0, qty - (frm.doc.total_delivered || 0)));
    }
});
