import frappe
from frappe.utils import cint


def run():
    frappe.connect()
    try:
        from library_management.www.library import get_context
        context = frappe._dict()
        get_context(context)
        print("get_context OK, books:", len(context.books))
        for b in context.books[:3]:
            print(f"  {b.name}: borrowed={b.library_total_borrows}, last={b.last_borrowed_display}")
    except Exception as e:
        import traceback
        traceback.print_exc()
    frappe.destroy()