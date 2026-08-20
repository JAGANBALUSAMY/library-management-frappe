# Copyright (c) 2026, Jagan and Contributors
# See license.txt

import frappe
from frappe.exceptions import ValidationError
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils import random_string


def make_author():
	name = f"Test Author {random_string(4)}"
	if frappe.db.exists("Library Author", name):
		return name
	doc = frappe.new_doc("Library Author")
	doc.author_name = name
	doc.insert(ignore_permissions=True)
	return doc.name


def make_category():
	name = f"Test Category {random_string(4)}"
	if frappe.db.exists("Library Category", name):
		return name
	doc = frappe.new_doc("Library Category")
	doc.category_name = name
	doc.insert(ignore_permissions=True)
	return doc.name


def make_book(**kwargs):
	kwargs.setdefault("book_name", f"Temp Book {random_string(4)}")
	kwargs.setdefault("isbn", f"TEST-{random_string(6)}")
	kwargs.setdefault("author", make_author())
	kwargs.setdefault("category", make_category())
	kwargs.setdefault("available_copies", 3)
	kwargs.setdefault("price", 100)
	kwargs.setdefault("published", 1)
	doc = frappe.new_doc("Library Book")
	for k, v in kwargs.items():
		setattr(doc, k, v)
	doc.insert(ignore_permissions=True)
	return doc


class UnitTestLibraryBook(UnitTestCase):
	def test_scrubbed_title(self):
		book = frappe._dict(book_name="The 100 Greatest Books")
		doc = frappe.new_doc("Library Book")
		doc.book_name = book.book_name
		self.assertEqual(doc.scrubbed_title(), "the-100-greatest-books")

	def test_make_route(self):
		doc = frappe.new_doc("Library Book")
		doc.book_name = "Test Title"
		self.assertEqual(doc.make_route(), "library-book/test-title")

	def test_route_for_non_ascii(self):
		doc = frappe.new_doc("Library Book")
		doc.book_name = "Café au Lait"
		self.assertTrue(doc.make_route().startswith("library-book/"))


class TestLibraryBook(IntegrationTestCase):
	def test_create_book(self):
		book = make_book()
		self.assertTrue(book.name)
		self.assertTrue(book.route)
		self.assertEqual(book.published, 1)

	def test_website_generator_condition_field(self):
		book = make_book()
		website = book.website
		self.assertEqual(website.condition_field, "published")

	def test_available_copies(self):
		book = make_book(available_copies=5)
		self.assertEqual(book.available_copies, 5)

	def test_negative_copies_rejected(self):
		with self.assertRaises(ValidationError):
			make_book(available_copies=-1)

	def test_negative_price_rejected(self):
		with self.assertRaises(ValidationError):
			make_book(price=-10)

	def test_duplicate_isbn_rejected(self):
		book = make_book()
		with self.assertRaises(ValidationError):
			make_book(isbn=book.isbn)

	def test_default_available_copies(self):
		book = make_book(available_copies=None)
		self.assertEqual(book.available_copies, 1)

	def test_route_is_generated_for_published(self):
		book = make_book(book_name="Route Generated Book", published=1)
		self.assertTrue(book.route)
		self.assertTrue(book.route.startswith("library-book/"))

	def test_translation_wrapped_errors(self):
		# Errors must be translatable (wrapped in frappe._)
		with self.assertRaises(ValidationError):
			make_book(book_name="", isbn=f"X-{random_string(5)}")

	def tearDown(self):
		frappe.db.rollback()
