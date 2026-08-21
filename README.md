Library Management

Library Management System built with Frappe Framework v16.

Assignment: Basics Python API

This assignment demonstrates document lifecycle management and safely extending DocType behavior using Controllers and Hooks in Frappe.

Part 1 — Controller Lifecycle

A custom Test Document DocType was created with a Description field.

The generated Python controller was extended using the before_save() lifecycle method.

class TestDocument(Document):

    def before_save(self):

        if not self.description:

            self.description = "Default Description"

When a Test Document is saved without a Description, Frappe automatically sets:

Default Description

The generated controller structure and type annotations are managed by Frappe and were not manually modified.

Part 2 — Safe Overrides Using Hooks

The standard Frappe behavior is extended through the application's hooks.py without modifying Frappe core files.

The Test Document DocType uses the after_insert document event:

doc_events = {

    "Test Document": {

        "after_insert": "library_management.api.custom_logic",

    },

}

The corresponding custom function is defined in library_management/api.py:

def custom_logic(doc, method):

    frappe.msgprint("Hook executed!")

When a new Test Document is created, the after_insert event triggers the custom function and displays:

Hook executed!

Concepts Demonstrated

DocType Controller

before_save lifecycle event

doc_events hooks

after_insert document event

Custom Python functions

frappe.msgprint()

Extending Frappe behavior without modifying core framework files

Assignment: Python API — Document, Database & Query Builder

This assignment demonstrates the use of Frappe's Whitelisted API, Query Builder, Document API, and Database API.

Part 1 — Custom Whitelisted API

Created a whitelisted Python method in the Test Document controller.

@frappe.whitelist()
def document_api_demo(related_document):

Part 2 — Query Builder

Used frappe.qb to join Test Document and Test Related Document and retrieve the required fields.

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

Part 3 — Document API

Used frappe.get_doc() to fetch a Test Document, update its description, and save it.

first_document = frappe.get_doc(
    "Test Document",
    results[0]["test_document"]
)

first_document.description = "Updated using Document API"
first_document.save()

Part 4 — Database API

Used frappe.db.set_value() to update the status of the related documents.

for row in results:
    frappe.db.set_value(
        "Test Related Document",
        row["related_document"],
        "status",
        "Processed",
        update_modified=False,
    )

Part 5 — Desk Trigger

Added a Run Document API button to the Test Related Document form to trigger the whitelisted Python method.

frappe.call({
    method: "library_management.custom_module.doctype.test_document.test_document.document_api_demo",
    args: {
        related_document: frm.doc.name
    }
});

The API updates the status from:

Pending → Processed

and updates the linked Test Document description using the Document API.

Concepts Demonstrated

@frappe.whitelist()

Query Builder (frappe.qb)

Query Builder JOIN

frappe.get_doc()

Document .save()

frappe.db.set_value()

Client Script

frappe.call()

Working with related DocTypes

Returning API results

Installation

You can install this app using the Bench CLI:

cd $PATH_TO_YOUR_BENCH

bench get-app $URL_OF_THIS_REPO --branch version-16

bench --site $SITE_NAME install-app library_management

License

MIT