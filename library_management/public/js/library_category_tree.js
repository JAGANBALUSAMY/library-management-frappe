frappe.treeview_settings['Library Category'] = {
    // 11. frappe.treeview_settings
    
    // Ignore these fields when adding a new node
    ignore_fields: ["description"],
    
    // Setup fields for the New Node dialog
    get_tree_nodes: 'frappe.desk.treeview.get_children',
    add_tree_node: 'frappe.desk.treeview.add_node',
    
    // Custom buttons on the tree view page
    toolbar: [
        {
            label:__("Print Categories"),
            condition: function() { return true; },
            click: function() {
                frappe.msgprint(__("Printing category tree..."));
            }
        }
    ],
    
    // Called when a node is selected
    onrender: function(node) {
        if(node.data.value === 'Science Fiction') {
            node.$tree_link.css('font-weight', 'bold');
        }
    }
};

/* 
 * NOTE: For this JS to actually execute, the Library Category DocType 
 * MUST have `is_tree` = 1 checked in its DocType definition, and 
 * it must have `parent_library_category`, `old_parent`, `lft`, `rgt` fields.
 * Since we are demonstrating the API without forcing major DB schema changes,
 * this file serves as the correct implementation reference.
 */
