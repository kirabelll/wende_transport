frappe.ui.form.on("Vehicle", {
    refresh(frm) {
        if (frm.doc.compliance_locked) {
            frm.dashboard.set_headline_alert(
                __("⚠️ Compliance Alert: This vehicle is LOCKED ({0})", [frm.doc.lock_reason]),
                "red"
            );
            frm.add_custom_button(__("Unlock Vehicle"), () => {
                frappe.confirm(__("Are you sure you want to unlock vehicle {0}?", [frm.doc.plate_number]), () => {
                    frm.call("unlock_vehicle").then(() => frm.reload_doc());
                });
            }, __("Actions"));
        } else {
            frm.add_custom_button(__("Create Trip"), () => {
                frappe.new_doc("Trip", {
                    vehicle: frm.doc.name,
                    driver: frm.doc.assigned_driver
                });
            }, __("Actions"));
        }

        frm.add_custom_button(__("View Trips"), () => {
            frappe.set_route("List", "Trip", { vehicle: frm.doc.name });
        }, __("History"));

        frm.add_custom_button(__("Maintenance Orders"), () => {
            frappe.set_route("List", "Work Order", { vehicle: frm.doc.name });
        }, __("History"));

        frm.add_custom_button(__("Fuel Logs"), () => {
            frappe.set_route("List", "Fuel Log", { vehicle: frm.doc.name });
        }, __("History"));
    }
});
