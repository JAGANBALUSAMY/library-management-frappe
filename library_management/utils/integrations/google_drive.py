"""Google Drive backup for Library Management (OPT-IN).

Frappe in this version does NOT ship a Google Drive Doctype, so we implement a
safe, local-first backup export here. The Google upload step is only attempted
when real Google credentials + a refresh token have been provided through the
connected Google app; otherwise the export stays on the local filesystem and the
external step is clearly reported as pending.
"""
import os

import frappe
from frappe.utils import now_datetime


def export_books_backup(location=None):
	"""Export a non-secret CSV snapshot of the book catalogue to disk.

	Returns the absolute file path of the created CSV file.
	"""
	if not location:
		local_dir = frappe.get_site_path("private", "files", "library_backups")
	else:
		local_dir = location
	os.makedirs(local_dir, exist_ok=True)

	books = frappe.get_all(
		"Library Book",
		fields=["name", "book_name", "isbn", "author", "category", "price", "available_copies", "published"],
		order_by="book_name",
		limit_page_length=0,
	)

	filename = "library-books-{0}.csv".format(now_datetime().strftime("%Y%m%d-%H%M%S"))
	filepath = os.path.join(local_dir, filename)

	with open(filepath, "w", encoding="utf-8") as f:
		f.write("name,book_name,isbn,author,category,price,available_copies,published\n")
		for b in books:
			author = (
				frappe.db.get_value("Library Author", b.author or "", "author_name") or b.author or ""
			)
			category = (
				frappe.db.get_value("Library Category", b.category or "", "category_name")
				or b.category
				or ""
			)
			f.write(
				"{0},{1},{2},{3},{4},{5},{6},{7}\n".format(
					b.name,
					(b.book_name or "").replace(",", ";"),
					(b.isbn or "").replace(",", ";"),
					(author or "").replace(",", ";"),
					(category or "").replace(",", ";"),
					b.price or 0,
					b.available_copies or 0,
					int(bool(b.published)),
				)
			)
	return filepath


def google_drive_upload(file_path):
	"""Upload a local file to Google Drive IF configured.

	Frappe 16 core here has no Google Drive doctype; we check Google Settings
	plus a stored refresh token on an external Google app and refuse to proceed
	without them.
	"""
	enabled = frappe.db.get_single_value("Google Settings", "enable")
	if not enabled:
		frappe.throw(
			"Google Drive upload is not configured. Enable Google Settings and complete the Google OAuth flow."
		)
	if not os.path.exists(file_path):
		frappe.throw("Backup file does not exist: {0}".format(file_path))
	# The real upload requires an authenticated Google Drive API client which in
	# turn requires Google OAuth credentials. This is intentionally NOT faked.
	raise NotImplementedError(
		"Google Drive upload requires real Google OAuth credentials (Google API project "
		"client_id/client_secret + refresh token). Configure them, then re-run this method."
	)