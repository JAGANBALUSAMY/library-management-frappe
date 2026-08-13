import frappe


def run():
    frappe.connect()
    for name in frappe.get_all("Library Book", filters={"book_name": ["like", "Temp%"]}, pluck="name"):
        frappe.delete_doc("Library Book", name, force=True)
    for name in frappe.get_all("Library Borrow Record", filters={"name": ["like", "LIB-BRW-0003%"]}, pluck="name"):
        frappe.delete_doc("Library Borrow Record", name, force=True)
    frappe.db.commit()
    print("cleanup done")
    frappe.destroy()
