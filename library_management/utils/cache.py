"""Safe caching helpers for Library Management.

Dynamic portal data (available book counts, borrow stats) is cheap and user
specific, so the portal controllers use ``context.no_cache`` and we never share
the public cache across users.

One genuinely useful cache key: total available-published book count used by the
context processor. It is invalidated as soon as a Library Book or a Library
Borrow Record changes.
"""
import frappe

AVAILABLE_COUNT_KEY = "library_available_published_count"


def available_published_count():
	"""Return the number of published books that currently have stock."""
	count = frappe.cache.get_value(AVAILABLE_COUNT_KEY)
	if count is None:
		count = frappe.db.count(
			"Library Book",
			{"published": 1, "available_copies": (">", 0)},
		)
		frappe.cache.set_value(AVAILABLE_COUNT_KEY, count, expires_in_sec=30)
	return count


def invalidate_library_count(*args, **kwargs):
	"""Hook handler: drop the cached count whenever books or borrows change."""
	frappe.cache.delete_key(AVAILABLE_COUNT_KEY)


def invalidate_on_borrow_change(doc, method=None, *args, **kwargs):
	return invalidate_library_count(doc, method, *args, **kwargs)


def invalidate_on_book_change(doc, method=None, *args, **kwargs):
	return invalidate_library_count(doc, method, *args, **kwargs)