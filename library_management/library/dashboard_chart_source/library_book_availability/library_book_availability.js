frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Library Book Availability"] = {
	method: "library_management.library.dashboard_chart_source.library_book_availability.library_book_availability.get_data",
};
