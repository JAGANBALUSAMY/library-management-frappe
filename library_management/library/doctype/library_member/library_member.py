# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class LibraryMember(Document):
    def validate(self):
        if not self.member_name:
            frappe.throw(_("Member Name is mandatory"))
        
        # Example validation
        if self.email and "@" not in self.email:
            frappe.throw(_("Please enter a valid email address"))

    def after_insert(self):
        # Create an introductory log or send a welcome email in the background
        msg = f"New Member Registered: {self.member_name}"
        print(msg)
        frappe.msgprint(msg)
