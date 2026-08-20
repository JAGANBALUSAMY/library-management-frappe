# Copyright (c) 2026, Jagan and Contributors
# See license.txt

import frappe
from frappe.model.document import Document


class LibraryRazorpaySettings(Document):
	@frappe.whitelist()
	def clear_secrets(self):
		"""Scrub stored secrets (used by tests)."""
		self.api_secret = ""
		self.webhook_secret = ""
		self.save(ignore_permissions=True)
		return True