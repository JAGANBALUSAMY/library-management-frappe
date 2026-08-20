"""Dashboard Chart configuration for Library Management.

Two charts, both using supported Frappe feature sets:

Chart 1 — Library Borrow Statistics : "Group By" chart over Borrow Record status
                                       (rendered as a Donut).
Chart 2 — Library Book Availability  : "Custom" chart backed by a
                                       Dashboard Chart Source (JS + whitelisted
                                       get_data). Shows Available vs Out-of-stock
                                       published books.
"""
import frappe

BORROW_STATS_CHART = "Library Borrow Statistics"
AVAILABILITY_CHART = "Library Book Availability"
AVAILABILITY_SOURCE = "Library Book Availability"


def create_charts():
	"""Create/update the two dashboard charts (idempotent)."""
	create_borrow_stats_chart()
	create_availability_source()
	create_availability_chart()
	return True


def _create_dashboard_chart(name, data):
	if frappe.db.exists("Dashboard Chart", name):
		return frappe.get_doc("Dashboard Chart", name)
	doc = frappe.new_doc("Dashboard Chart")
	doc.update(data)
	doc.filters_json = "[]"
	doc.insert(ignore_permissions=True)
	return doc


def create_borrow_stats_chart():
	doc = _create_dashboard_chart(
		BORROW_STATS_CHART,
		{
			"chart_name": BORROW_STATS_CHART,
			"chart_type": "Group By",
			"document_type": "Library Borrow Record",
			"group_by_type": "Count",
			"group_by_based_on": "status",
			"type": "Donut",
			"is_public": 1,
			"module": "Library",
		},
	)
	doc.chart_type = "Group By"
	doc.group_by_based_on = "status"
	doc.save(ignore_permissions=True)
	return doc


def create_availability_source():
	"""Register the Dashboard Chart Source used by the custom availability chart."""
	if frappe.db.exists("Dashboard Chart Source", AVAILABILITY_SOURCE):
		return frappe.get_doc("Dashboard Chart Source", AVAILABILITY_SOURCE)
	doc = frappe.new_doc("Dashboard Chart Source")
	doc.source_name = AVAILABILITY_SOURCE
	doc.module = "Library"
	doc.insert(ignore_permissions=True)
	return doc


def create_availability_chart():
	if frappe.db.exists("Dashboard Chart", AVAILABILITY_CHART):
		return frappe.get_doc("Dashboard Chart", AVAILABILITY_CHART)
	doc = _create_dashboard_chart(
		AVAILABILITY_CHART,
		{
			"chart_name": AVAILABILITY_CHART,
			"chart_type": "Custom",
			"source": AVAILABILITY_SOURCE,
			"type": "Donut",
			"is_public": 1,
			"module": "Library",
		},
	)
	return doc


def resolve_book_availability_data():
	"""Directly resolve the availability chart dataset (used by tests)."""
	from library_management.library.dashboard_chart_source.library_book_availability.library_book_availability import (
		get_data,
	)

	return get_data(chart_name=AVAILABILITY_CHART)


def verify_charts():
	"""Return a list of (test_name, result_bool, detail) for the verification suite."""
	results = []
	borrow = frappe.db.exists("Dashboard Chart", BORROW_STATS_CHART)
	results.append(("Borrow stats chart exists", bool(borrow), BORROW_STATS_CHART))
	if borrow:
		doc = frappe.get_doc("Dashboard Chart", BORROW_STATS_CHART)
		results.append(("Borrow stats chart type", doc.chart_type == "Group By", doc.chart_type))
		results.append(
			("Borrow stats group by status", doc.group_by_based_on == "status", doc.group_by_based_on)
		)
	avail = frappe.db.exists("Dashboard Chart", AVAILABILITY_CHART)
	results.append(("Availability chart exists", bool(avail), AVAILABILITY_CHART))
	src = frappe.db.exists("Dashboard Chart Source", AVAILABILITY_SOURCE)
	results.append(("Availability source exists", bool(src), AVAILABILITY_SOURCE))
	if avail:
		doc = frappe.get_doc("Dashboard Chart", AVAILABILITY_CHART)
		results.append(("Availability chart is Custom", doc.chart_type == "Custom", doc.chart_type))
		results.append(("Availability source linked", doc.source == AVAILABILITY_SOURCE, doc.source))
	try:
		data = resolve_book_availability_data()
		results.append(
			(
				"Availability data resolves",
				bool(data.get("labels")) and bool(data.get("datasets")),
				data,
			)
		)
	except Exception as e:
		results.append(("Availability data resolves", False, str(e)))
	return results