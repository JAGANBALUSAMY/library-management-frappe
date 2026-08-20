"""Razorpay integration for Library Management (membership/fine payment).

This bench ships only the legacy ``frappe.integrations.payment_gateways.razorpay``
module with no Razorpay Settings DocType. We therefore provide:

* a small Library Razorpay Settings single DocType (api_key/api_secret kept in
  Password fields),
* a guarded ``create_payment_request`` that requires the settings doc to exist
  AND the gateway to be enabled with a real API key. Without real credentials
  the method raises a clear error (never fakes a payment).
"""
import frappe
from frappe import _

REALM = "Library Razorpay Settings"


def get_settings():
	return frappe.get_single("Library Razorpay Settings")


def is_configured():
	"""True only when a real API key is present (never invent one)."""
	try:
		settings = get_settings()
	except frappe.DoesNotExistError:
		return False
	return bool(settings.enabled and settings.api_key and settings.api_secret)


def create_payment_request(amount, description, reference_dt=None, reference_dn=None):
	"""Create a Razorpay-aware payment request record.

	Raises when the gateway is not configured. With a configured gateway it
	stores a ``Library Payment Request`` (local doc) that a librarian can then
	process through the Razorpay dashboard/API.
	"""
	if not is_configured():
		frappe.throw(
			_("Razorpay is not configured. Set the API Key/Secret in {0} and enable it.").format(REALM)
		)
	doc = frappe.new_doc("Library Payment Request")
	doc.amount = amount
	doc.description = description
	doc.reference_dt = reference_dt or ""
	doc.reference_dn = reference_dn or ""
	doc.status = "Draft"
	doc.insert(ignore_permissions=True)
	return doc


def verify_razorpay_structure():
	"""Structural verification (no credentials used)."""
	return {
		"settings_doctype": REALM,
		"settings_exists": bool(frappe.db.exists("DocType", "Library Razorpay Settings")),
		"record_doctype": "Library Payment Request",
		"record_doctype_exists": bool(frappe.db.exists("DocType", "Library Payment Request")),
		"configured": is_configured(),
	}