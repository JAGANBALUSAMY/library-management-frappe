# Copyright (c) 2026, Jagan and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import random_string

from library_management.library.doctype.library_borrow_record.library_borrow_record import (
	LibraryBorrowWorkflow,
	STATUS_ISSUED,
	STATUS_OVERDUE,
	STATUS_PENDING,
	STATUS_RETURNED,
)

MEMBER1 = "member1@library.local"
MEMBER2 = "member2@library.local"
LIBRARIAN = "librarian@library.local"


def make_member(email=None, name=None, end_date=None):
	email = email or f"member-{random_string(4)}@example.com"
	name = name or f"Member {random_string(4)}"
	if frappe.db.exists("Library Member", {"email": email}):
		return frappe.db.get_value("Library Member", {"email": email}, "name")
	doc = frappe.new_doc("Library Member")
	doc.member_name = name
	doc.email = email
	doc.status = "Active"
	doc.membership_date = frappe.utils.today()
	doc.end_date = end_date or frappe.utils.add_days(frappe.utils.today(), 365)
	doc.insert(ignore_permissions=True)
	return doc.name


def make_borrow(member, book, status=STATUS_PENDING, **kwargs):
	doc = frappe.new_doc("Library Borrow Record")
	doc.member = member
	doc.library_book = book
	doc.status = status
	for k, v in kwargs.items():
		setattr(doc, k, v)
	doc.insert(ignore_permissions=True)
	return doc


def _book(**kwargs):
	from library_management.library.doctype.library_book.test_library_book import make_book

	return make_book(**kwargs)


class UnitTestLibraryBorrowRecord(UnitTestCase):
	def test_default_dates(self):
		doc = frappe.new_doc("Library Borrow Record")
		doc.set_default_dates()
		self.assertTrue(doc.borrow_date)
		self.assertTrue(doc.due_date)
		from frappe.utils import add_days

		self.assertEqual(doc.due_date, add_days(doc.borrow_date, 14))


class TestLibraryBorrowRecord(IntegrationTestCase):
	def setUp(self):
		self.member1 = make_member(email=MEMBER1, name="Member One")
		self.member2 = make_member(email=MEMBER2, name="Member Two")

	def test_create_pending(self):
		book = _book(available_copies=3)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		self.assertEqual(rec.status, STATUS_PENDING)
		self.assertTrue(rec.borrow_date)
		self.assertTrue(rec.due_date)

	def test_default_status_and_dates(self):
		book = _book(available_copies=2)
		doc = frappe.new_doc("Library Borrow Record")
		doc.member = self.member1
		doc.library_book = book.name
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.status, STATUS_PENDING)
		self.assertTrue(doc.borrow_date and doc.due_date)

	def test_out_of_stock_rejected(self):
		book = _book(available_copies=0)
		with self.assertRaises(ValidationError):
			make_borrow(self.member1, book.name, status=STATUS_PENDING)

	def test_unpublished_book_rejected(self):
		book = _book(available_copies=5, published=0)
		with self.assertRaises(ValidationError):
			make_borrow(self.member1, book.name, status=STATUS_PENDING)

	def test_member_cannot_borrow_for_other_member(self):
		book = _book(available_copies=2)
		frappe.set_user(MEMBER1)
		try:
			with self.assertRaises(ValidationError):
				make_borrow(self.member2, book.name, status=STATUS_PENDING)
		finally:
			frappe.set_user("Administrator")

	def test_expired_membership_rejected(self):
		book = _book(available_copies=2)
		member = make_member(email=f"expired-{random_string(4)}@example.com", end_date=frappe.utils.add_days(frappe.utils.today(), -1))
		with self.assertRaises(ValidationError):
			make_borrow(member, book.name, status=STATUS_PENDING)

	def test_workflow_issue_decrements_stock(self):
		book = _book(available_copies=2)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		frappe.db.set_value("Library Book", book.name, "available_copies", 2)
		issued = LibraryBorrowWorkflow.issue(rec.name)
		self.assertEqual(issued.status, STATUS_ISSUED)
		self.assertEqual(frappe.db.get_value("Library Book", book.name, "available_copies"), 1)

	def test_workflow_return_restores_stock(self):
		book = _book(available_copies=2)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		frappe.db.set_value("Library Book", book.name, "available_copies", 2)
		issued = LibraryBorrowWorkflow.issue(rec.name)
		returned = LibraryBorrowWorkflow.return_book(issued.name)
		self.assertEqual(returned.status, STATUS_RETURNED)
		self.assertTrue(returned.return_date)
		self.assertEqual(frappe.db.get_value("Library Book", book.name, "available_copies"), 2)

	def test_workflow_overdue(self):
		book = _book(available_copies=1)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		issued = LibraryBorrowWorkflow.issue(rec.name)
		overdue = LibraryBorrowWorkflow.mark_overdue(issued.name)
		self.assertEqual(overdue.status, STATUS_OVERDUE)

	def test_invalid_transition_rejected(self):
		book = _book(available_copies=1)
		rec = make_borrow(self.member1, book.name, status=STATUS_RETURNED, return_date=frappe.utils.today())
		with self.assertRaises(ValidationError):
			LibraryBorrowWorkflow.issue(rec.name)

	def test_issue_out_of_stock_rejected(self):
		book = _book(available_copies=0)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		frappe.db.set_value("Library Book", book.name, "available_copies", 0)
		rec.reload()
		with self.assertRaises(ValidationError):
			LibraryBorrowWorkflow.issue(rec.name)

	def test_guest_denied_permission(self):
		conditions = frappe.get_attr(
			"library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions"
		)("Guest")
		self.assertEqual(conditions, "1=0")

	def test_member_only_sees_own_records(self):
		book = _book(available_copies=2)
		rec = make_borrow(self.member1, book.name, status=STATUS_PENDING)
		conditions = frappe.get_attr(
			"library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions"
		)(MEMBER1)
		self.assertTrue(conditions.startswith("member ="))

	def test_librarian_sees_all_records(self):
		conditions = frappe.get_attr(
			"library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions"
		)(LIBRARIAN)
		self.assertEqual(conditions, "")

	def tearDown(self):
		frappe.db.rollback()
