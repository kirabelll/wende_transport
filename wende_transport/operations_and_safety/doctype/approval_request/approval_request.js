frappe.ui.form.on("Approval Request", {
    refresh(frm) {
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__("Approve Request"), () => {
                frappe.confirm(__("Confirm approval for {0}?", [frm.doc.name]), () => {
                    frm.call("approve").then(() => frm.reload_doc());
                });
            }, __("Decision")).addClass("btn-success");

            frm.add_custom_button(__("Reject Request"), () => {
                frappe.prompt([
                    { fieldname: "reason", fieldtype: "Small Text", label: __("Rejection Reason"), reqd: 1 }
                ], (values) => {
                    frm.call("reject", { reason: values.reason }).then(() => frm.reload_doc());
                }, __("Reject Approval Request"), __("Reject"));
            }, __("Decision")).addClass("btn-danger");
        }
    }
});
