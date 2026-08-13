"""Installation hooks for library_management."""
import frappe


def after_install():
    """Create custom fields after app installation."""
    create_custom_fields()


def create_custom_fields():
    """Create custom fields on Library Book for library-specific tracking.

    Idempotent: uses update=True so re-running does not duplicate fields.
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    custom_fields = {
        "Library Book": [
            {
                "fieldname": "library_section_tracking",
                "fieldtype": "Section Break",
                "label": "Library Tracking",
                "insert_after": "published",
            },
            {
                "fieldname": "library_last_borrowed",
                "fieldtype": "Datetime",
                "label": "Last Borrowed",
                "read_only": 1,
                "insert_after": "library_section_tracking",
            },
            {
                "fieldname": "library_total_borrows",
                "fieldtype": "Int",
                "label": "Total Borrows",
                "read_only": 1,
                "default": "0",
                "insert_after": "library_last_borrowed",
            },
        ]
    }

    create_custom_fields(custom_fields, update=True)
