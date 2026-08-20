"""Provision Dev Guide artifacts for library_management (idempotent).

Run with:
    bench --site <site> execute library_management.setup_devguides.create_all

Creates: dashboard charts + chart source, webhook, OAuth client/provider,
Social Login Key (Google), LDAP Settings placeholder, Razorpay Settings,
Translation fixtures.
"""
import frappe
from frappe import _


def create_all():
	create_translations()
	create_charts()
	create_webhook()
	create_oauth()
	create_social_login_key()
	create_ldap_settings()
	create_razorpay_settings()
	frappe.db.commit()
	print("library_management dev guides setup complete")


def create_translations():
	from library_management.utils.translations import install_sample_translations

	return install_sample_translations()


def create_charts():
	from library_management.utils.charts import create_charts

	return create_charts()


def create_webhook():
	import json

	webhook_name = "Library Borrow Record Webhook"
	payload = json.dumps(
		{
			"borrow_record": "{{ doc.name }}",
			"member": "{{ doc.member }}",
			"book": "{{ doc.library_book }}",
			"borrow_date": "{{ doc.borrow_date }}",
			"due_date": "{{ doc.due_date }}",
			"return_date": "{{ doc.return_date or '' }}",
			"status": "{{ doc.status }}",
		},
		indent=4,
	)

	if frappe.db.exists("Webhook", webhook_name):
		doc = frappe.get_doc("Webhook", webhook_name)
		doc.request_data = payload
		doc.save(ignore_permissions=True)
		return doc

	doc = frappe.new_doc("Webhook")
	doc.name = webhook_name
	doc.webhook_doctype = "Library Borrow Record"
	doc.webhook_doctype_event = "on_update"
	doc.request_url = "http://127.0.0.1:9999/library-webhook"  # local test receiver
	doc.request_method = "POST"
	doc.request_structure = "Form URL-Encoded"
	doc.request_data = payload
	doc.request_headers = []
	doc.insert(ignore_permissions=True)
	return doc


def create_oauth():
	if not frappe.db.exists("OAuth Provider Settings"):
		settings = frappe.new_doc("OAuth Provider Settings")
		settings.skip_authorization = 1
		settings.save(ignore_permissions=True)

	client_name = "library-management-demo-client"
	if not frappe.db.exists("OAuth Client", {"app_name": "Library Management Demo Client"}):
		client = frappe.new_doc("OAuth Client")
		client.app_name = "Library Management Demo Client"
		client.default_redirect_uri = "http://localhost:8000/api/method/frappe.integrations.oauth2.redirect_uri"
		client.redirect_uris = "http://localhost:8000/api/method/frappe.integrations.oauth2.redirect_uri\nhttp://localhost:8000/oauth/callback"
		client.response_type = "Code"
		client.grant_type = "Authorization Code"
		client.scopes = "all openid"
		client.skip_authorization = 1
		client.user = "Administrator"
		client.insert(ignore_permissions=True)
	return True


def create_social_login_key():
	if frappe.db.exists("Social Login Key", "google"):
		return frappe.get_doc("Social Login Key", "google")
	doc = frappe.new_doc("Social Login Key")
	doc.provider_name = "Google"
	doc.name = "google"
	doc.enable_social_login = 0  # cannot enable without real credentials
	doc.social_login_provider = "Google"
	doc.client_id = ""
	doc.client_secret = ""
	doc.base_url = "https://accounts.google.com"
	doc.authorize_url = "https://accounts.google.com/o/oauth2/auth"
	doc.access_token_url = "https://accounts.google.com/o/oauth2/token"
	doc.redirect_url = "http://localhost:8000/api/method/frappe.integrations.oauth2_logins.google_login"
	doc.user_id_property = "email"
	doc.api_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
	doc.icon = "assets/frappe/icons/social/google.svg"
	doc.insert(ignore_permissions=True)
	return doc


def create_ldap_settings():
	from library_management.utils.integrations.ldap import create_placeholder_settings

	return create_placeholder_settings()


def create_razorpay_settings():
	doctype = "Library Razorpay Settings"
	if frappe.db.exists("DocType", doctype) and frappe.db.exists(doctype):
		return frappe.get_doc(doctype)
	doc = frappe.new_doc(doctype)
	doc.enabled = 0
	doc.api_key = ""
	doc.api_secret = ""
	doc.insert(ignore_permissions=True)
	return doc