import frappe

from library_management.utils.cache import available_published_count


def library_context(context):
	context.library_name = "Frappe Library"
	context.available_book_count = available_published_count()
	return context