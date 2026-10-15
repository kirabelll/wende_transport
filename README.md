# Wende Transport (Frappe Framework Version-15)

Enterprise Fleet, Dispatch, Maintenance, Fuel, Tyre, Rental, and Operations Management custom app built for **Frappe Framework v15**.

This app is a full-featured transport operations platform based on `samaria-transport-backend` and `samaria-transport-frontend`, retaining core fleet, dispatch, workshop, fuel, tyre, partner fleet, and operations workflows, with general ledger accounting, procurement, stores, and cashiering excluded as specified.

---

## 🌟 Key Functional Domains & Modules

The application is structured into **11 registered Frappe modules**:

| Module | Core DocTypes | Key Responsibilities |
| :--- | :--- | :--- |
| **Fleet Management** | `Vehicle`, `Vehicle Category`, `Vehicle Pairing`, `Driver Assignment`, `Km Log` | Tractor & trailer registries, compliance locking (insurance, road fund, fitness, inspection), telematics, pairing, and odometer tracking. |
| **Dispatch & Logistics** | `Customer`, `Rate Contract`, `Customer Order`, `Order Revision`, `Order Penalty`, `Trip`, `Trip Status History`, `Vehicle Swap Log` | Automated ton-based rate contracts, customer credit checks, real-time trip status workflow, weighbridge & POD reconciliation, shortage calculation, and profit proration. |
| **Driver Management** | `Transport Employee`, `Driver Advance`, `Driver Ledger Entry`, `Driver Score`, `Driver Reward Penalty`, `Reward Penalty Rule`, `Vehicle Handover`, `Handover Checklist Item` | Driver licensing, trip advance disbursement & recovery, dynamic 100-point performance scorecards, reward/penalty points, digital vehicle handovers. |
| **Maintenance & Workshop** | `Garage`, `Breakdown Report`, `Work Order`, `Maintenance Schedule`, `Maintenance Class Template` | In-house and outsourced workshop work orders, labor and parts cost aggregation, downtime tracking, preventive maintenance schedules (A/B/C services). |
| **Fuel Management** | `Fuel Log`, `Fuel Standard` | Fuel refill logs, trip expense allocation, standard vs actual km/L variance reporting, and fuel theft detection. |
| **Tyre Management** | `Tyre Asset`, `Tyre History` | Tyre lifecycle tracking, fitment/removal km, retread counting, and Cost Per Kilometer (CPK) calculation. |
| **Rental Fleet** | `Rental Owner`, `Rental Vehicle`, `Rental Trip`, `Rental Payment` | Outsourced vehicle operations, rate difference proration (client rate vs owner rate), owner balance tracking, and company margin calculation. |
| **Revenue Sharing** | `Revenue Share Contract`, `Revenue Share Trip`, `Revenue Share Settlement` | Joint venture & tractor-trailer revenue sharing models, expense deduction prior to percentage split. |
| **Broker Management** | `Transport Broker`, `Broker Commission` | Cargo broker registry, commission percentage/flat fee calculation per trip, and broker payout balances. |
| **Operations & Safety** | `Accident Record`, `Operations Alert`, `Alert Rule`, `Approval Request`, `Approval Rule`, `Company Legal Document`, `Contract Expiry` | Accident incident reports, proactive operations alerts (insurance expiry, overdue work orders, missing PODs > 3 days), and rule-based approval routing. |
| **Integrations** | `Telegram Config`, `Telegram Log` | Telegram Bot notifications for critical events (accidents, emergency breakdowns, critical compliance expirations). |



---

## 🚫 Note on Excluded Accounting

As requested, general ledger double-entry bookkeeping (`Account`, `JournalEntry`, `FiscalPeriod`, chart of accounts) has been excluded. All operational cash flows are instead managed through:
- **Cashier Tills & Petty Cash Sessions** (physical till tracking, daily limits, cash reconciliations).
- **Transport Payment Requests** (multi-tier approvals, trip advances, workshop bills, supplier payments).
- **Transport Invoices & Payments** (customer billing, invoice aging, outstanding balances).
- **Driver Advances & Recoveries** (trip advance balances tracked on driver ledgers).

---

## ⚙️ Backend API & Scheduled Tasks

The Python API in `wende_transport/api/` exposes whitelisted endpoints and background automation:

1. **`wende_transport.api.trips`**:
   - `validate_trip`, `on_trip_update`: Odometer validation, vehicle status locking, trip cost aggregation.
   - `suggest_assignment`: Intelligent dispatch algorithm scoring available vehicles by idle time, driver score, category match, and maintenance status.
   - `get_trip_kpis`: Tonnage moved, revenue, cost, profit, and delivery shortage statistics.

2. **`wende_transport.api.vehicles`**:
   - `get_fleet_board`: Real-time Kanban-style fleet overview grouped by status (`Available`, `On Trip`, `Maintenance`, `Breakdown`).
   - `check_compliance_expiry_all`: Daily check marking vehicles `Maintenance` if insurance, inspection, or road fund has expired.

3. **`wende_transport.api.alerts`**:
   - `evaluate_operations_alerts`: Automated scanner checking:
     - Missing PODs on trips completed > 3 days ago.
     - Vehicle document expiries (due in <= 7 days or overdue).
     - Driver license expirations.
     - Spare parts below reorder level.
     - Overdue workshop work orders.
     - Dispatches Telegram alerts for High and Critical severities.

4. **`wende_transport.api.cashier`**:
   - `get_cashier_summary`: Till balances, active sessions, today's disbursements and receipts.
   - `open_session`, `close_session`: Validates active sessions and calculates physical count variance.

5. **`wende_transport.api.drivers`**:
   - `recalculate_driver_scores`: Computes 0-100 composite safety and delivery performance scores.
   - `get_driver_leaderboard`: Ranks top-performing drivers for incentive rewards.

6. **`wende_transport.api.dashboard`**:
   - `get_executive_kpis`: Executive metrics across Fleet, Logistics, Cash, Workshop, and Safety.

7. **`wende_transport.api.reports`**:
   - `get_trip_profitability_report`: Trip revenue, fuel, driver advance, shortage cost, net profit, margin %.
   - `get_fuel_efficiency_report`: Actual km/L vs standard km/L, fuel spend, variance %.
   - `get_tyre_cost_per_km_report`: Tyre CPK calculation.
   - `get_rental_fleet_margin_report`: Outsourced fleet billing, owner payout, company margin %.

---

## 🚀 Installation & Site Setup

### Prerequisites
- Frappe Framework v15
- Python 3.10+
- MariaDB 10.6+ or PostgreSQL 14+
- Node.js 18+

### Step 1: Install App into Bench
```bash
# From your frappe-bench directory:
bench get-app /path/to/wende_transport
# Or if cloning from git:
# bench get-app https://github.com/your-org/wende-transport.git
```

### Step 2: Install into Your Site
```bash
bench --site [your-site-name] install-app wende_transport
```

Upon installation, `wende_transport.setup.after_install` automatically seeds:
- System Roles (`Fleet Manager`, `Dispatcher`, `Technical Manager`, `Store Manager`, `Cashier`, `Operations Manager`, `Safety Officer`)
- Standard Vehicle Categories
- Preventive Maintenance Class Templates (`A-Service`, `B-Service`, `C-Service`)
- Standard Digital Handover Checklist Items
- Automated Operations Alert Rules & Approval Rules

### Step 3: Run Migrations & Build Assets
```bash
bench --site [your-site-name] migrate
bench build --app wende_transport
```

---

## 🖥️ Desk Workspaces & Collapsible Dropdown Structure

The app uses **one single parent workspace (`Wende Transport`)** with all operational modules nested as a collapsible dropdown list in the Frappe Desk sidebar (via Frappe's native `parent_page` hierarchy):

```
📁 Wende Transport [^]
   ├── 🚛 Fleet Management
   ├── 🧭 Dispatch & Logistics
   ├── 👥 Driver Management
   ├── 🔧 Maintenance & Workshop
   ├── ⛽ Fuel Management
   ├── ⭕ Tyre Management
   ├── 🤝 Rental Fleet
   ├── 📊 Revenue Sharing
   ├── 👤 Broker Management
   ├── 🛡️ Operations & Safety
   └── 🔗 Integrations & Telegram
```

---

## 🔒 Security & Roles

Role-Based Access Control (RBAC) is configured across all DocTypes:
- **Fleet Manager**: Full management of vehicles, pairing, km logs, and handover verification.
- **Dispatcher**: Orders, rate contracts, trips, vehicle swap logs, weighbridge reconciliation.
- **Technical Manager**: Garages, breakdown reports, work orders, tyre assets, maintenance schedules.
- **Operations Manager**: High-value approvals, company legal documents, contract expiries, alerts review.
- **Driver**: Vehicle handover checklists, driver score viewing.

