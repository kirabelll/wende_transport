import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TyreAsset(Document):
    def validate(self):
        fit_km = flt(self.fitment_km)
        rem_km = flt(self.removal_km)
        cost = flt(self.purchase_cost)

        if rem_km > fit_km:
            self.total_km_run = rem_km - fit_km
        elif self.current_vehicle:
            veh = frappe.get_doc("Vehicle", self.current_vehicle)
            if flt(veh.current_km) > fit_km:
                self.total_km_run = flt(veh.current_km) - fit_km

        if self.total_km_run > 0 and cost > 0:
            self.cost_per_km = round(cost / self.total_km_run, 4)
