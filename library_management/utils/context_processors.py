import frappe

def library_context(context):
	context.library_name = "Frappe Library"
	context.available_book_count = frappe.db.count(
		"Library Book", {"published": 1, "available_copies": (">", 0)}
	)
	return context
