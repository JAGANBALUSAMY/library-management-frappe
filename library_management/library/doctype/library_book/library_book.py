# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

class LibraryBook(WebsiteGenerator):
    website = frappe._dict(
        condition_field = "published"
    )

    def before_naming(self):
        """Trim spaces before Frappe assigns the name"""
        if self.book_name:
            self.book_name = self.book_name.strip()

    def before_validate(self):
        """Format data before logic checks."""
        if self.book_name:
            self.book_name = self.book_name.title() # Capitalize Each Word

    def validate(self):
        """Main validation logic. Throws errors to stop execution."""
        super().validate()  # WebsiteGenerator.validate -> generates the website route

        if not self.book_name:
            frappe.throw(_("Book Name is required."))

        if self.price is not None and self.price < 0:
            frappe.throw(_("Price cannot be negative."))
            
        if self.available_copies is not None and self.available_copies < 0:
            frappe.throw(_("Available Copies cannot be negative."))

        self.validate_duplicate_isbn()

    def make_route(self):
        """Generate a unique website route for each published book."""
        return f"library-book/{self.scrubbed_title()}"

    def validate_duplicate_isbn(self):
        """Ensure ISBN is unique across all books"""
        if self.isbn:
            exists = frappe.db.exists(
                "Library Book",
                {
                    "isbn": self.isbn,
                    "name": ["!=", self.name]
                }
            )
            if exists:
                frappe.throw(_("A book with ISBN {0} already exists.").format(self.isbn))

    def before_save(self):
        """Set default calculated values before DB write."""
        if self.available_copies is None:
            self.available_copies = 1

    def after_insert(self):
        """Run actions after the row is physically in the DB."""
        msg = f"New Book Added: {self.name}"
        print(msg)
        frappe.msgprint(msg)

    def on_trash(self):
        """Run logic when document is deleted."""
        pass