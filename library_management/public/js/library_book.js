frappe.ui.form.on('Library Book', {
    refresh: function(frm) {
        if(frm.fields_dict.book_name) {
            frm.fields_dict.book_name.$input.css('background-color', '#e8f5e9');
        }

        // --- TASK 1 & 15: Custom Button + AJAX Call ---
        frm.add_custom_button(__('Check Availability'), function() {
            frappe.call({
                method: 'library_management.api.get_book_details',
                args: { book_name: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        var d = r.message;
                        var html = frappe.render_template(
                            '<div style="padding:10px;">' +
                            '<h4>{{ book_name }}</h4>' +
                            '<p><strong>Author:</strong> {{ author_name }}</p>' +
                            '<p><strong>ISBN:</strong> {{ isbn }}</p>' +
                            '<p><strong>Available Copies:</strong> {{ available_copies }}</p>' +
                            '<p><strong>Status:</strong> ' +
                            '{% if availability === "Available" %}' +
                            '<span style="color:green;font-weight:bold;">Available</span>' +
                            '{% else %}' +
                            '<span style="color:red;font-weight:bold;">Unavailable</span>' +
                            '{% endif %}</p>' +
                            '</div>',
                            d
                        );
                        frappe.msgprint({
                            title: __('Book Availability'),
                            indicator: d.availability === 'Available' ? 'green' : 'red',
                            message: html
                        });
                    }
                }
            });
        }, __('Actions'));

        // --- TASK 15: Quick Borrow via frappe.call ---
        frm.add_custom_button(__('Quick Borrow'), function() {
            var d = new frappe.ui.Dialog({
                title: __('Enter details to borrow'),
                fields: [
                    {
                        label: __('Member'),
                        fieldname: 'member',
                        fieldtype: 'Link',
                        options: 'Library Member',
                        reqd: 1
                    }
                ],
                size: 'small',
                primary_action_label: __('Borrow'),
                primary_action(values) {
                    frappe.call({
                        method: 'library_management.api.borrow_book',
                        args: {
                            member_id: values.member,
                            book_id: frm.doc.name
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: __('Successfully borrowed by {0}!', [values.member]),
                                    indicator: 'green'
                                });
                                frm.reload_doc();
                                d.hide();
                            }
                        }
                    });
                }
            });
            d.show();
        }, __('Actions'));

        frm.add_custom_button(__('View Borrow History'), function() {
            frappe.set_route('List', 'Library Borrow Record', { library_book: frm.doc.name });
        }, __('Actions'));

        frm.add_custom_button(__('Report Lost'), function() {
            frappe.confirm(
                __('Are you sure you want to mark this book as lost?'),
                function() {
                    frappe.prompt([{
                        label: __('Reason for Loss'),
                        fieldname: 'reason',
                        fieldtype: 'Data',
                        reqd: 1
                    }], function(values) {
                        frappe.call({
                            method: 'frappe.client.set_value',
                            args: {
                                doctype: 'Library Book',
                                name: frm.doc.name,
                                fieldname: 'available_copies',
                                value: 0
                            },
                            callback: function() {
                                frappe.show_alert({
                                    message: __('Book marked as lost. Reason: {0}', [values.reason]),
                                    indicator: 'red'
                                });
                                frm.reload_doc();
                            }
                        });
                    }, __('Provide Details'), __('Submit'));
                }
            );
        }, __('Actions'));

        // --- TASK 9: HTML Template availability preview ---
        if (frm.doc.name && !frm.is_new()) {
            frappe.call({
                method: 'library_management.api.get_book_details',
                args: { book_name: frm.doc.name },
                callback: function(r) {
                    if (r.message) {
                        var d = r.message;
                        var html = frappe.render_template(
                            '<div class="library-availability-card" style="border:1px solid #e0e0e0;border-radius:8px;padding:12px;margin-top:10px;background:#f8f9fa;">' +
                            '<h5 style="margin:0 0 8px;">Book Availability</h5>' +
                            '<p style="margin:2px 0;"><strong>Title:</strong> {{ book_name }}</p>' +
                            '<p style="margin:2px 0;"><strong>Author:</strong> {{ author_name }}</p>' +
                            '<p style="margin:2px 0;"><strong>Available Copies:</strong> {{ available_copies }}</p>' +
                            '<p style="margin:2px 0;"><strong>Status:</strong> ' +
                            '{% if availability === "Available" %}' +
                            '<span style="color:green;font-weight:bold;">Available</span>' +
                            '{% else %}' +
                            '<span style="color:red;font-weight:bold;">Unavailable</span>' +
                            '{% endif %}</p>' +
                            '</div>',
                            d
                        );
                        frm.set_df_property('availability_preview', 'options', html);
                    }
                }
            });
        }
    },

    onload: function(frm) {
        frappe.realtime.on('book_borrowed', function(data) {
            if(data.book === frm.doc.book_name) {
                frappe.show_alert(__('Heads up! {0} just borrowed a copy of this book.', [data.member]));
                frm.reload_doc();
            }
        });
    }
});
