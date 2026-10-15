frappe.ui.form.on("Work Order", {
    refresh(frm) {
        if (frm.doc.status === "Open") {
            frm.add_custom_button(__("Start Work"), () => {
                frm.set_value("status", "In Progress");
                frm.set_value("start_time", frappe.datetime.now_datetime());
                frm.save();
            }, __("Action")).addClass("btn-warning");
        } else if (frm.doc.status === "In Progress") {
            frm.add_custom_button(__("Complete Work Order"), () => {
                frm.set_value("status", "Completed");
                frm.set_value("end_time", frappe.datetime.now_datetime());
                frm.save();
            }, __("Action")).addClass("btn-success");
        }

        frm.add_custom_button(__("Request Spare Parts"), () => {
            frappe.new_doc("Spare Part Request", {
                work_order: frm.doc.name
            });
        }, __("Store"));
    },

    labor_cost(frm) {
        frm.trigger("calculate_totals");
    },
    parts_cost(frm) {
        frm.trigger("calculate_totals");
    },
    calculate_totals(frm) {
        let labor = frm.doc.labor_cost || 0;
        let parts = frm.doc.parts_cost || 0;
        frm.set_value("total_cost", labor + parts);
    }
});
