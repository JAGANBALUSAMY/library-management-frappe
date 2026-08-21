# Copyright (c) 2026, Jagan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TestDocument(Document):

    def before_save(self):
        if not self.description:
            self.description = "Default Description"


@frappe.whitelist()
def document_api_demo(related_document):
    TestDocument = frappe.qb.DocType("Test Document")
    TestRelatedDocument = frappe.qb.DocType("Test Related Document")

    results = (
        frappe.qb.from_(TestDocument)
        .join(TestRelatedDocument)
        .on(TestRelatedDocument.test_document == TestDocument.name)
        .select(
            TestDocument.name.as_("test_document"),
            TestDocument.description,
            TestRelatedDocument.name.as_("related_document"),
            TestRelatedDocument.status,
        )
        .where(TestRelatedDocument.name == related_document)
        .limit(10)
        .run(as_dict=True)
    )

    if results:
        first_document = frappe.get_doc(
            "Test Document",
            results[0]["test_document"]
        )

        first_document.description = "Updated using Document API"
        first_document.save()

    for row in results:
        frappe.db.set_value(
            "Test Related Document",
            row["related_document"],
            "status",
            "Processed",
            update_modified=False,
        )

    return results