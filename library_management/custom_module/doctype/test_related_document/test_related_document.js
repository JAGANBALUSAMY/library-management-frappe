frappe.ui.form.on("Test Related Document", {
    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        frm.add_custom_button("Run Document API", () => {
            frappe.call({
                method: "library_management.custom_module.doctype.test_document.test_document.document_api_demo",
                args: {
                    related_document: frm.doc.name
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint({
                            title: "API Executed",
                            message: "Document API and Database API executed successfully.",
                            indicator: "green"
                        });

                        frm.reload_doc();
                    }
                }
            });
        });
    }
});