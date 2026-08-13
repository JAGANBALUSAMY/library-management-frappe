frappe.listview_settings['Library Book'] = {
    add_fields: ["available_copies"],

    get_indicator: function(doc) {
        if (doc.available_copies > 0) {
            return [__("Available"), "green", "available_copies,>,0"];
        } else {
            return [__("Out of Stock"), "red", "available_copies,=,0"];
        }
    },

    onload: function(listview) {
        listview.page.add_inner_button(__("Sync All Inventory"), function() {
            frappe.call({
                method: "library_management.api.start_inventory_sync",
                callback: function(r) {
                    frappe.msgprint(__("Inventory sync triggered in the background!"));
                }
            });
        });
    }
};
