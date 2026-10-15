frappe.provide("frappe.wende");

frappe.wende = {
  format_currency: function(val) {
    return (parseFloat(val) || 0).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }) + " ETB";
  },

  format_tons: function(val) {
    return (parseFloat(val) || 0).toFixed(2) + " Tons";
  },

  format_km: function(val) {
    return (parseFloat(val) || 0).toLocaleString("en-US") + " Km";
  },

  check_operations_alerts: function() {
    frappe.call({
      method: "wende_transport.api.dashboard.get_executive_kpis",
      callback: function(r) {
        if (r.message && r.message.safety_and_alerts) {
          const crit = r.message.safety_and_alerts.critical_alerts;
          if (crit > 0) {
            frappe.show_alert({
              message: __("Attention: You have {0} critical Operations Alert(s) requiring action.", [crit]),
              indicator: "red"
            }, 7);
          }
        }
      }
    });
  }
};

$(document).on("app_ready", function() {
  // Check critical alerts on desk ready if user has operational roles
  if (frappe.user && frappe.user_roles.some(r => ["System Manager", "Fleet Manager", "Operations Manager", "Dispatcher"].includes(r))) {
    setTimeout(function() {
      frappe.wende.check_operations_alerts();
    }, 2500);
  }
});
