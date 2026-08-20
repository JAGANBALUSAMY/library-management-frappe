"""Library calendar events -> Google Calendar (OPT-IN).

Frappe ships a Google Calendar integration (Google Settings + Google Calendar
doc + connected OAuth app). We use it only when it is actually configured:
when the Google Calendar document for the user has enable=1 AND a refresh token
is stored, updating an Event can be pushed to Google.

Whatever we do here never fabricates a Google sync: without valid credentials
the local Frappe Event is created and the external push is skipped.
"""
import frappe
from frappe import _

EVENT_SUBJECT = "Library Book Due"


def sync_borrow_due_date(doc, method=None, *args, **kwargs):
	"""Doc-event hook: create (or update) a local Event for the due date.

	Registered in ``hooks.py`` under ``doc_events`` for
	``Library Borrow Record.on_update``.
	"""
	if not doc:
		return None
	if not getattr(doc, "due_date", None):
		return None
	member = frappe.db.get_value("Library Member", doc.member, "member_name") or doc.member
	book = frappe.db.get_value("Library Book", doc.library_book, "book_name") or doc.library_book
	subject = "{0}: {1} -> {2}".format(_(EVENT_SUBJECT), book, member)

	event = frappe.db.get_value(
		"Event",
		{"custom_library_borrow_record": doc.name},
		"name",
		order_by="creation desc",
	)
	event_data = {
		"subject": subject,
		"starts_on": doc.due_date,
		"event_type": "Private",
		"status": "Open",
		"custom_library_borrow_record": doc.name,
	}
	if doc.get("status") == "Returned":
		event_data["status"] = "Closed"
	if event:
		frappe.db.set_value("Event", event, event_data)
		return event
	ev = frappe.new_doc("Event")
	ev.update(event_data)
	ev.flags.ignore_permissions = True
	ev.insert()
	return ev.name


def try_google_calendar_push(record_name):
	"""Enqueue a Google Calendar push only when credentials exist and the
	integration is enabled. Never called with fake credentials."""
	enabled = frappe.db.get_single_value("Google Settings", "enable")
	if not enabled:
		return False
	cal = frappe.db.get_value("Google Calendar", {"user": frappe.session.user, "enable": 1}, "name")
	if not cal or not frappe.db.get_value("Google Calendar", cal, "refresh_token"):
		return False
	doc = frappe.get_doc("Google Calendar", cal)
	if not doc.refresh_token:
		return False
	frappe.enqueue(
		"library_management.utils.integrations.google_calendar._push_calendar",
		calendar_name=cal,
		record_name=record_name,
		enqueue_after_commit=True,
	)
	return True


def _push_calendar(calendar_name, record_name):
	event = sync_borrow_due_date(frappe.get_doc("Library Borrow Record", record_name))
	if not event:
		return False
	cal = frappe.get_doc("Google Calendar", calendar_name)
	if not getattr(cal, "refresh_token", None):
		return False
	# Real external sync requires a valid refresh token (Google Workspace project).
	cal.push()  # type: ignore[attr-defined]
	return True