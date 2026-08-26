# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

from frappe import _


def execute(filters=None):
    columns = [
        {
            "label": _("Book Name"),
            "fieldname": "book_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Author"),
            "fieldname": "author",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Issue Date"),
            "fieldname": "issue_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Book Price"),
            "fieldname": "book_price",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]

    data = [
        {
            "book_name": "Python Basics",
            "author": "John Smith",
            "issue_date": "2026-08-20",
            "book_price": 450,
        },
        {
            "book_name": "Learning Frappe",
            "author": "David Miller",
            "issue_date": "2026-08-22",
            "book_price": 650,
        },
        {
            "book_name": "Database Fundamentals",
            "author": "Robert Wilson",
            "issue_date": "2026-08-25",
            "book_price": 550,
        },
    ]

    return columns, data