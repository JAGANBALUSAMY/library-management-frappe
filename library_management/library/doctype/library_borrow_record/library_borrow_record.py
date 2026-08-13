# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

LIBRARIAN_ROLES = ("Librarian", "Library Manager", "Library Administrator", "System Manager")

STATUS_PENDING = "Pending"
STATUS_ISSUED = "Issued"
STATUS_RETURNED = "Returned"
STATUS_OVERDUE = "Overdue"

ALLOWED_TRANSITIONS = {
	STATUS_PENDING: {STATUS_ISSUED},
	STATUS_ISSUED: {STATUS_RETURNED, STATUS_OVERDUE},
	STATUS_OVERDUE: {STATUS_RETURNED},
	STATUS_RETURNED: set(),
}


def _member_for_user(user=None):
	"""Return the Library Member record linked to a user (by email), if any."""
	if not user:
		user = frappe.session.user
	if user == "Guest":
		return None
	return frappe.db.get_value("Library Member", {"email": user}, "name")


def get_permission_query_conditions(user=None):
	"""Server-side row-level filter for Library Borrow Record.

	- Guest: no rows
	- Librarian roles: all rows
	- Library Member: only their own member's rows
	- Otherwise: no rows
	"""
	if not user:
		user = frappe.session.user

	if user == "Guest":
		return "1=0"

	if any(role in frappe.get_roles(user) for role in LIBRARIAN_ROLES):
		return ""

	member = _member_for_user(user)
	if member:
		return f"member = {frappe.db.escape(member)}"

	return "1=0"


def has_permission(doc, ptype="read", user=None, verbose=False):
	"""Server-side row-level permission for an individual document."""
	if not user:
		user = frappe.session.user

	if user == "Guest":
		return False

	if any(role in frappe.get_roles(user) for role in LIBRARIAN_ROLES):
		return True

	if not doc:
		return True

	member = _member_for_user(user)
	if member:
		return doc.member == member

	return False


class LibraryBorrowRecord(Document):
	def validate(self):
		self.validate_required_fields()
		self.validate_dates()
		self.validate_member_allowed()
		self.validate_book_availability()
		self.validate_status_transition()
		self.apply_status_stock_changes()

	def _is_librarian(self, user=None):
		if not user:
			user = frappe.session.user
		return any(role in frappe.get_roles(user) for role in LIBRARIAN_ROLES)

	def before_save(self):
		if not self.status:
			self.status = STATUS_PENDING

	def validate_required_fields(self):
		if not self.member:
			frappe.throw(_("Member is required to create a borrow request."))
		if not self.library_book:
			frappe.throw(_("Please select a book to borrow."))
		if not self.borrow_date:
			frappe.throw(_("Borrow Date is required to create a borrow request."))
		if not self.due_date:
			frappe.throw(_("Please provide a due date (return date) for the borrowed book."))

	def validate_dates(self):
		if self.due_date and self.borrow_date and self.due_date < self.borrow_date:
			frappe.throw(
				_("The due date ({0}) cannot be earlier than the borrow date ({1}).").format(
					self.due_date, self.borrow_date
				)
			)

	def validate_member_allowed(self):
		"""A plain Library Member may only create/update their own borrow records."""
		user = frappe.session.user
		if user == "Guest":
			return

		if any(role in frappe.get_roles(user) for role in LIBRARIAN_ROLES):
			return

		member = _member_for_user(user)
		if not member:
			frappe.throw(
				_("You do not have a valid library membership. Please contact the librarian.")
			)
		if self.member != member:
			frappe.throw(
				_("You can only create borrow requests for your own membership ({0}).").format(member)
			)

	def validate_book_availability(self):
		if not self.library_book:
			return

		# Only re-validate the book when the request is new or the book is being
		# changed. This allows a librarian to mark a book as returned later even
		# if the book has since gone out of stock.
		if not (self.is_new() or self.meta.has_value_changed("library_book")):
			return

		book = frappe.get_doc("Library Book", self.library_book)
		if not book.published:
			frappe.throw(
				_("The book '{0}' is not available for borrowing because it is not published.").format(
					book.book_name
				)
			)
		if (book.available_copies or 0) <= 0:
			frappe.throw(
				_("The book '{0}' is currently out of stock.").format(book.book_name)
			)

	def validate_status_transition(self):
		"""Enforce who may approve and the valid status lifecycle:
		Pending -> Issued -> Returned/Overdue.

		- Only a librarian may issue, return or mark a request overdue.
		- A Library Member can only create (Pending) records.
		"""
		old_status = None
		if not self.is_new():
			old_status = frappe.db.get_value(self.doctype, self.name, "status")
		self._old_status = old_status

		new_status = self.status or STATUS_PENDING

		if not self._is_librarian():
			if new_status in {STATUS_ISSUED, STATUS_RETURNED, STATUS_OVERDUE}:
				frappe.throw(
					_("Only a librarian can change the status of a borrow request to '{0}'.").format(
						new_status
					)
				)

		if old_status and old_status != new_status:
			if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
				frappe.throw(
					_("Status cannot be changed from '{0}' to '{1}'.").format(old_status, new_status)
				)

	def apply_status_stock_changes(self):
		"""Adjust book stock when a request is issued or returned."""
		old_status = getattr(self, "_old_status", None)
		if old_status == self.status:
			return

		if self.status == STATUS_ISSUED and old_status != STATUS_ISSUED:
			self.adjust_book_stock(-1, _("Not enough copies of '{0}' available to issue."))
		elif self.status == STATUS_RETURNED and old_status in (STATUS_ISSUED, STATUS_OVERDUE):
			self.adjust_book_stock(1, _("Could not return '{0}' - stock update failed."))

	def adjust_book_stock(self, delta, error_msg):
		if not self.library_book:
			return
		book = frappe.get_doc("Library Book", self.library_book)
		new_available = (book.available_copies or 0) + delta
		if new_available < 0:
			frappe.throw(error_msg.format(book.book_name))
		frappe.db.set_value("Library Book", book.name, "available_copies", new_available)

	def has_website_permission(self, ptype, user, verbose=False):
		# A public user (Guest) cannot access any borrow records
		if user == "Guest":
			return False

		return has_permission(self, ptype=ptype, user=user, verbose=verbose)
