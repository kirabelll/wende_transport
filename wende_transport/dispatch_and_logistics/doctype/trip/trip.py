import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds, flt

STATUS_TRANSITIONS = {
    "Planned": ["Dispatched", "Cancelled"],
    "Dispatched": ["Loading", "Cancelled"],
    "Loading": ["In Transit", "Cancelled"],
    "In Transit": ["Delivering", "Cancelled"],
    "Delivering": ["Completed", "Cancelled"],
    "Completed": [],
    "Cancelled": []
}

VEHICLE_STATUS_MAP = {
    "Dispatched": "On Trip",
    "Loading": "Loading",
    "In Transit": "On Trip",
    "Delivering": "On Trip",
    "Completed": "Idle",
    "Cancelled": "Idle"
}

class Trip(Document):
    def validate(self):
        self.enforce_vehicle_compliance()
        self.enforce_customer_credit()
        self.calculate_shortage_and_revenue()
        self.calculate_cycle_time()
        self.calculate_profitability()

    def enforce_vehicle_compliance(self):
        if self.vehicle:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            if veh.compliance_locked:
                frappe.throw(f"Vehicle {veh.plate_number} is compliance-locked: {veh.lock_reason}. Renew documents before dispatching.")

    def enforce_customer_credit(self):
        if self.status == "Dispatched" and self.customer:
            cust = frappe.get_doc("Customer", self.customer)
            if cust.dispatch_blocked:
                frappe.throw(f"Cannot dispatch trip: Customer {cust.company_name} is blocked ({cust.block_reason or 'overdue balance'}).")

    def calculate_shortage_and_revenue(self):
        loaded = flt(self.loaded_quantity_tons) or flt(self.planned_quantity_tons)
        delivered = flt(self.delivered_quantity_tons)
        rate = flt(self.rate_per_ton)

        if delivered > 0:
            self.shortage = max(0.0, loaded - delivered)
            self.revenue = delivered * rate
            self.shortage_deduction = self.shortage * rate
            
            if self.customer_deducted:
                if not self.customer_deduction_amount:
                    self.customer_deduction_amount = self.shortage_deduction
            else:
                self.customer_deduction_amount = 0.0

            if self.shortage > 0 and not self.driver_penalty_amount:
                self.driver_penalty_amount = self.shortage_deduction

    def calculate_cycle_time(self):
        if self.departure_time and self.unloading_end_time:
            secs = time_diff_in_seconds(self.unloading_end_time, self.departure_time)
            self.total_cycle_minutes = int(secs / 60) if secs > 0 else 0

    def calculate_profitability(self):
        fuel = flt(self.allocated_fuel_cost) or flt(self.fuel_cost)
        maint = flt(self.allocated_maintenance_cost)
        depr = flt(self.allocated_depreciation_cost)
        driver = flt(self.allocated_driver_cost)
        self.total_trip_cost = fuel + maint + depr + driver
        if self.revenue:
            self.profit_per_trip = flt(self.revenue) - self.total_trip_cost

    def on_update(self):
        # 1. Update vehicle operational status
        if self.vehicle and self.status in VEHICLE_STATUS_MAP:
            veh = frappe.get_doc("Vehicle", self.vehicle)
            target_status = VEHICLE_STATUS_MAP[self.status]
            if not veh.compliance_locked and veh.operational_status != target_status:
                veh.operational_status = target_status
                veh.save(ignore_permissions=True)

        # 2. Update linked Customer Order delivery progress
        if self.order:
            order_doc = frappe.get_doc("Customer Order", self.order)
            order_doc.update_delivery_progress()

        # 3. If completed with shortage, post driver penalty to Driver Ledger
        if self.status == "Completed" and flt(self.shortage) > 0 and flt(self.driver_penalty_amount) > 0 and self.driver:
            self.create_driver_shortage_penalty()

    def create_driver_shortage_penalty(self):
        existing = frappe.get_all("Driver Ledger Entry", filters={"reference_id": self.name, "category": "shortage"})
        if not existing:
            # Get latest balance
            last_entry = frappe.get_all("Driver Ledger Entry", filters={"driver": self.driver}, fields=["balance"], order_by="creation desc", limit=1)
            prev_balance = last_entry[0].balance if last_entry else 0.0
            penalty = flt(self.driver_penalty_amount)
            new_balance = prev_balance - penalty

            doc = frappe.get_doc({
                "doctype": "Driver Ledger Entry",
                "driver": self.driver,
                "type": "Debit",
                "category": "shortage",
                "amount": penalty,
                "balance": new_balance,
                "reference_type": "Trip",
                "reference_id": self.name,
                "description": f"Shortage penalty: {self.shortage:.2f} tons on Trip {self.name} (ETB {penalty:,.2f})"
            })
            doc.insert(ignore_permissions=True)

    @frappe.whitelist()
    def dispatch_trip(self):
        if self.status != "Planned":
            frappe.throw("Only Planned trips can be dispatched")
        self.status = "Dispatched"
        self.save()

    @frappe.whitelist()
    def start_loading(self, loaded_quantity=None):
        if self.status != "Dispatched":
            frappe.throw("Only Dispatched trips can move to Loading")
        self.status = "Loading"
        self.loading_start_time = now_datetime()
        if loaded_quantity:
            self.loaded_quantity_tons = flt(loaded_quantity)
        self.save()

    @frappe.whitelist()
    def mark_in_transit(self, loaded_quantity=None):
        if loaded_quantity:
            self.loaded_quantity_tons = flt(loaded_quantity)
        if not self.loaded_quantity_tons or self.loaded_quantity_tons <= 0:
            frappe.throw("Cannot move to In Transit: Loaded quantity must be recorded first.")
        self.status = "In Transit"
        self.departure_time = now_datetime()
        self.save()

    @frappe.whitelist()
    def close_trip(self, delivered_quantity, notes=None, customer_deducted=0, customer_deduction_amount=0, driver_penalty_amount=0):
        if not delivered_quantity or flt(delivered_quantity) <= 0:
            frappe.throw("Delivered quantity is required to complete the trip.")
        self.delivered_quantity_tons = flt(delivered_quantity)
        self.customer_deducted = 1 if customer_deducted else 0
        self.customer_deduction_amount = flt(customer_deduction_amount)
        self.driver_penalty_amount = flt(driver_penalty_amount)
        if notes:
            self.notes = (self.notes or "") + "\n" + notes
        self.unloading_end_time = now_datetime()
        self.status = "Completed"
        self.save()
        return self.name
