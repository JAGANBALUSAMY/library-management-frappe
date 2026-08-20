# Copyright (c) 2026, Jagan and Contributors
# License: MIT. See license.txt

import frappe
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get_data(
	chart_name: str | None = None,
	chart: str | None = None,
	no_cache: str | None = None,
	filters: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	timespan: str | None = None,
	time_interval: str | None = None,
	heatmap_year: str | None = None,
):
	"""Available vs Out-of-stock published books (custom dashboard chart source)."""
	from frappe import _

	available = frappe.db.count("Library Book", {"published": 1, "available_copies": (">", 0)})
	out_of_stock = frappe.db.count("Library Book", {"published": 1, "available_copies": ("=", 0)})
	return {
		"labels": [_("Available"), _("Out of Stock")],
		"datasets": [
			{"name": _("Books"), "values": [available or 0, out_of_stock or 0]},
		],
	}