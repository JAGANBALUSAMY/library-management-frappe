import frappe


def daily_maintenance():
    frappe.log_error(
        "Daily maintenance task executed successfully.",
        "Library Management - Daily Maintenance"
    )