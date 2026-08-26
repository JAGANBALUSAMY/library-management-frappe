# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Book Name"),
			"fieldname": "book_name",
			"fieldtype": "Data",
		},
		{
			"label": _("Author"),
			"fieldname": "author",
			"fieldtype": "Data",
		},
		{
			"label": _("Issue Date"),
			"fieldname": "issue_date",
			"fieldtype": "Date",
		},
		{
			"label": _("Book Price"),
			"fieldname": "book_price",
			"fieldtype": "Currency",
		},
	]


def get_data(filters=None):
	data = [
		["Python Basics", "John Smith", "2026-08-20", 450],
		["Learning Frappe", "David Miller", "2026-08-22", 650],
		["Database Fundamentals", "Robert Wilson", "2026-08-25", 550],
	]

	if filters and filters.get("author"):
		data = [
			row for row in data
			if filters.get("author").lower() in row[1].lower()
		]

	return data