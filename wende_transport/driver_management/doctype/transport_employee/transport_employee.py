from frappe.model.document import Document

class TransportEmployee(Document):
    def validate(self):
        first = (self.first_name or "").strip()
        last = (self.last_name or "").strip()
        self.full_name = f"{first} {last}".strip()
