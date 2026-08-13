import frappe
import time

def before_book_save(doc, method):
    """
    doc_events hook: Executed before a Library Book is saved.
    """
    msg = f"Hook triggered: Saving {doc.book_name or 'Book'}"
    print(msg)
    frappe.msgprint(msg)
    print(f"HOOK EXECUTED: {doc.book_name}")

def daily_check():
    """
    scheduler_events hook: Executed daily.
    """
    msg = "Daily scheduler task executed."
    print(msg)
    frappe.msgprint(msg)

# --------------------------------------------------
# TOPIC 7: Background Jobs (Worker)
# --------------------------------------------------
def sync_books_from_supplier():
    msg = "Syncing inventory from supplier..."
    print(msg)
    frappe.msgprint(msg)
    # Simulating heavy network task that would block the browser if run synchronously
    time.sleep(5) 
    msg = "Sync complete!"
    print(msg)
    frappe.msgprint(msg)
