import frappe
from frappe import _

from library_management.library.doctype.library_borrow_record.library_borrow_record import (
    LIBRARIAN_ROLES,
)


def get_context(context):

    context.no_cache = 1
    context.title = "Borrow History"


    # =========================================================
    # Current User
    # =========================================================

    user = frappe.session.user

    is_librarian = False
    member = None


    # =========================================================
    # Determine User Role
    # =========================================================

    if user and user != "Guest":

        user_roles = frappe.get_roles(user)

        is_librarian = any(
            role in user_roles
            for role in LIBRARIAN_ROLES
        )


        # Find Library Member linked to logged-in user

        member = frappe.db.get_value(
            "Library Member",
            {
                "email": user
            },
            "name",
        )


    # =========================================================
    # Build Filters
    # =========================================================

    filters = {}


    # Normal member:
    # Show only their own borrow records.

    if not is_librarian:

        if not member:

            frappe.throw(
                _(
                    "You must be logged in as a "
                    "library member to view your "
                    "borrow history."
                ),
                frappe.PermissionError,
            )


        filters["member"] = member


    # Librarian:
    # No member filter, so they can see all records.


    # =========================================================
    # Get Borrow Records
    # =========================================================

    records = frappe.get_all(
        "Library Borrow Record",
        filters=filters,
        fields=[
            "name",
            "member",
            "library_book",
            "borrow_date",
            "due_date",
            "status",
        ],
        order_by="creation desc",
    )


    # =========================================================
    # Resolve Book Information
    # =========================================================

    for record in records:

        book = frappe.db.get_value(
            "Library Book",
            record.library_book,
            [
                "book_name",
                "author",
            ],
            as_dict=True,
        )


        if book:

            record.book_name = (
                book.book_name
                or record.library_book
            )

            record.author = (
                book.author
                or ""
            )

        else:

            record.book_name = (
                record.library_book
            )

            record.author = ""


    # =========================================================
    # Calculate Statistics
    # =========================================================

    stats = {
        "total": len(records),
        "Pending": 0,
        "Issued": 0,
        "Returned": 0,
        "Overdue": 0,
    }


    for record in records:

        status = record.status


        if status in stats:

            stats[status] += 1


    # =========================================================
    # Send Data to Template
    # =========================================================

    context.records = records

    context.is_librarian = is_librarian

    context.member = member

    context.stats = stats


    return context