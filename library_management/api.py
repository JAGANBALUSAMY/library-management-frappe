"""Library Management whitelisted API methods."""
import frappe
from frappe import _


@frappe.whitelist()
def borrow_book(member_id, book_id):
    """Create a borrow request for a member and book.

    Called by the Quick Borrow button on the Library Book form.
    Decrements available_copies and emits a realtime event.
    """
    book = frappe.get_doc("Library Book", book_id)
    member = frappe.get_doc("Library Member", member_id)

    if (book.available_copies or 0) <= 0:
        frappe.throw(_("Book '{0}' is out of stock.").format(book.book_name))

    if not book.published:
        frappe.throw(_("Book '{0}' is not published.").format(book.book_name))

    borrow_record = frappe.get_doc({
        "doctype": "Library Borrow Record",
        "member": member.name,
        "library_book": book.name,
        "borrow_date": frappe.utils.today(),
        "due_date": frappe.utils.add_days(frappe.utils.today(), 14),
        "status": "Pending",
    })
    borrow_record.insert(ignore_permissions=True)

    frappe.db.set_value("Library Book", book.name, "available_copies", (book.available_copies or 1) - 1)
    frappe.db.commit()

    frappe.publish_realtime("book_borrowed", {
        "book": book.book_name,
        "member": member.name,
        "record": borrow_record.name,
    })

    return {
        "borrow_record": borrow_record.name,
        "available_copies": book.available_copies - 1,
    }


@frappe.whitelist(allow_guest=True)
def start_inventory_sync():
    """Enqueue a background job to sync inventory from supplier.

    Called by the Sync All Inventory button on the Library Book list view.
    """
    frappe.enqueue(
        "library_management.tasks.sync_books_from_supplier",
        queue="long",
        timeout=60,
    )
    return {"status": "queued"}


@frappe.whitelist(allow_guest=True)
def get_book_details(book_name):
    """Return detailed book info including author name.

    Used by the Check Availability button and link field display.
    """
    book = frappe.get_all(
        "Library Book",
        filters={"name": book_name},
        fields=["name", "book_name", "isbn", "author", "category", "publisher",
                "price", "available_copies", "published"],
        limit=1,
    )
    if not book:
        return None

    b = book[0]
    if b.author:
        b.author_name = frappe.db.get_value("Library Author", b.author, "author_name") or b.author
    else:
        b.author_name = "Unknown"

    if b.category:
        b.category_name = frappe.db.get_value("Library Category", b.category, "category_name") or b.category
    else:
        b.category_name = ""

    if b.publisher:
        b.publisher_name = frappe.db.get_value("Library Publisher", b.publisher, "publisher_name") or b.publisher
    else:
        b.publisher_name = ""

    b.availability = "Available" if (b.available_copies or 0) > 0 and b.published else "Unavailable"
    return b
