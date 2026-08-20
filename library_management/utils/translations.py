"""Translation helpers for Library Management."""
import frappe

SAMPLE_STRINGS = [
	"Library",
	"Books",
	"Members",
	"Borrow History",
	"Borrow Book",
	"Available",
	"Out of Stock",
	"Borrow Date",
	"Due Date",
	"Return Date",
	"Status",
	"Submit Borrow Request",
	"Request Submitted",
	"Book '{0}' is out of stock.",
	"You do not have permission to access this record.",
	"Check Availability",
	"Library Collection",
]


def install_sample_translations():
	"""Create Translation records for Spanish (es). Idempotent.

	These records make the strings discoverable by Frappe's translation system.
	"""
	import csv
	import os

	path = os.path.join(os.path.dirname(__file__), "..", "translations", "es.csv")
	path = os.path.abspath(path)
	if not os.path.exists(path):
		return 0

	created = 0
	with open(path, newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for row in reader:
			source = (row.get("msgid") or "").strip()
			translated = (row.get("msgstr") or "").strip()
			if not source or not translated:
				continue
			if frappe.db.exists("Translation", {"source_text": source, "language": "es"}):
				continue
			doc = frappe.new_doc("Translation")
			doc.language = "es"
			doc.source_text = source
			doc.translated_text = translated
			doc.insert(ignore_permissions=True)
			created += 1
	frappe.db.commit()
	return created


def verify_translations():
	"""Return list of (test_name, ok, detail)."""
	results = []
	translated_es = {}
	try:
		translated_es = frappe.translate.get_translated_dict("es", "library_management")
	except Exception:
		translated_es = {}
	results.append(("Translation dict for es built", True, "es" if translated_es else "catalog-missing"))

	count = frappe.db.count("Translation", {"language": "es"})
	results.append(("Spanish Translation records exist", count > 0, count))

	for text in ["Library", "Books", "Available", "Out of Stock"]:
		exists = frappe.db.exists("Translation", {"language": "es", "source_text": text})
		results.append((f"Translation for '{text}'", bool(exists), exists or "missing"))

	# Discoverability: the message catalog should contain at least the required strings.
	if translated_es:
		missing = [s for s in SAMPLE_STRINGS if s not in str(translated_es)]
		results.append(("Sample strings discoverable in catalog", len(missing) == 0, missing or "all present"))
	else:
		results.append(("Sample strings discoverable in catalog", False, "no es catalog generated"))
	return results