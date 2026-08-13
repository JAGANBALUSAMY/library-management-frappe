import frappe
from frappe import _


def get_context(context):
	context.library_name = "Frappe Library"
	return context


@frappe.whitelist(allow_guest=True)
def get_member_for_user():
	# If there's a Member with the same email as the logged-in user, return it
	if frappe.session.user == "Guest":
		return None
	member = frappe.db.get_value("Library Member", {"email": frappe.session.user}, "name")
	return member


@frappe.whitelist(allow_guest=True)
def get_book_availability(book):
	"""Return availability info for a book. Used by the Web Form client script
	to validate the selected book before submission."""
	if not book:
		return {"book": None, "published": False, "available_copies": 0}

	book_doc = frappe.db.get_value(
		"Library Book",
		book,
		["name", "book_name", "published", "available_copies"],
		as_dict=True,
	)
	if not book_doc:
		return {"book": book, "published": False, "available_copies": 0}

	return {
		"book": book_doc.name,
		"book_name": book_doc.book_name,
		"published": bool(book_doc.published),
		"available_copies": book_doc.available_copies or 0,
	}


def get_list_context(context):
	# Do not allow guest to view the list of borrowing records via web form list view
	if frappe.session.user == "Guest":
		frappe.throw(_("You must be logged in to view borrowing records."))

	# Librarians see everything; members only see their own records.
	# Row-level filtering is enforced server-side by the
	# get_permission_query_conditions hook on Library Borrow Record.
	return context
