frappe.ui.form.on("Vehicle Handover", {
    refresh(frm) {
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__("Accept Handover"), () => {
                frappe.confirm(__("Confirm accepting vehicle handover to {0}?", [frm.doc.to_driver]), () => {
                    frm.set_value("status", "Accepted");
                    frm.save();
                });
            }, __("Action")).addClass("btn-success");

            frm.add_custom_button(__("Reject Handover"), () => {
                frappe.prompt([
                    { fieldname: "reason", fieldtype: "Small Text", label: __("Rejection Reason"), reqd: 1 }
                ], (values) => {
                    frm.set_value("status", "Rejected");
                    frm.set_value("rejection_reason", values.reason);
                    frm.save();
                }, __("Reject Handover"), __("Reject"));
            }, __("Action")).addClass("btn-danger");
        }
    },

    vehicle(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value("Vehicle", frm.doc.vehicle, ["assigned_driver", "current_km"], (r) => {
                if (r) {
                    if (r.assigned_driver && !frm.doc.from_driver) {
                        frm.set_value("from_driver", r.assigned_driver);
                    }
                    if (r.current_km && !frm.doc.km_reading) {
                        frm.set_value("km_reading", r.current_km);
                    }
                }
            });
        }
    }
});
