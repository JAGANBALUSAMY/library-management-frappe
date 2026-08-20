"""LDAP integration strategy for Library Management.

Frappe provides LDAP Settings (server URL, bind DN, user/group search,
group-role mapping, auto user creation). No real LDAP server is available in
this workspace, so we deliver:

* the correct Frappe-side structure to fill in,
* a validation routine that verifies the settings document shape,
* a clear manual configuration step (no fake credentials).
"""
import frappe


def get_ldap_settings():
	"""Return the LDAP Settings doc or None (without connecting)."""
	if frappe.db.get_single_value("LDAP Settings", "enabled") is not None:
		try:
			return frappe.get_doc("LDAP Settings")
		except frappe.DoesNotExistError:
			return None
	return None


def create_placeholder_settings():
	"""Create a DISABLED LDAP Settings record (no credentials)."""
	if frappe.db.exists("LDAP Settings"):
		return frappe.get_doc("LDAP Settings")
	doc = frappe.new_doc("LDAP Settings")
	doc.enabled = 0
	doc.ldap_server_url = ""  # your ldap.example.com:389
	doc.ldap_bind_dn = ""  # cn=admin,dc=library,dc=local
	doc.ldap_search_string = ""  # (uid={0})
	doc.ldap_user_creation_and_default_roles = 0
	doc.save(ignore_permissions=True)
	return doc


def validate_ldap_structure():
	"""Structural verification - never contacts an LDAP server."""
	meta = frappe.get_meta("LDAP Settings")
	has_required = all(
		meta.has_field(f)
		for f in (
			"ldap_server_url",
			"ldap_bind_dn",
			"ldap_password",
			"ldap_search_string",
			"ldap_search_path_user",
			"ldap_search_path_group",
		)
	)
	exists = frappe.db.exists("LDAP Settings")
	return {
		"doctype": "LDAP Settings",
		"exists": bool(exists),
		"has_required_structure_fields": has_required,
		"enabled": frappe.db.get_single_value("LDAP Settings", "enabled") if exists else 0,
	}