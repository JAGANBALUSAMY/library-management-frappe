"""Link field display formatters for Library Management.

Link fields normally render the document name (e.g. ``LIB-MEM-00001``).
These formatters show a friendly title together with the internal name, e.g::

	jane-smith — LIB-MEM-00001

Registered from the app ``hooks.py`` ``link_formatters`` dict.
"""

import frappe

TITLE_FIELD = {
	"Library Member": "member_name",
	"Library Author": "author_name",
	"Library Publisher": "publisher_name",
	"Library Book": "book_name",
}

URL_PREFIX = {
	"Library Member": "library-member",
	"Library Author": "library-author",
	"Library Publisher": "library-publisher",
	"Library Book": "library-book",
}


def format_link(doctype, docname, options):
	title_field = TITLE_FIELD.get(doctype)
	if not title_field or not docname:
		return None
	title = frappe.db.get_value(doctype, docname, title_field)
	if not title:
		return None
	label = f"{title} — {docname}"
	result = {"label": label}
	prefix = URL_PREFIX.get(doctype)
	if prefix:
		result["url"] = f"/app/{prefix}/{docname}"
	return result


def library_member(doctype, docname, options):
	return format_link(doctype, docname, options)


def library_author(doctype, docname, options):
	return format_link(doctype, docname, options)


def library_publisher(doctype, docname, options):
	return format_link(doctype, docname, options)


def library_book(doctype, docname, options):
	return format_link(doctype, docname, options)