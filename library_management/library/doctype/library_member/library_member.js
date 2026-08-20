// Copyright (c) 2026, Jagan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Library Member", {
    refresh(frm) {
        frm.add_custom_button("Send Welcome Email", () => {
            frappe.msgprint("Welcome email sent!");
        }, "Actions");
    }
});
