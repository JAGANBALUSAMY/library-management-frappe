frappe.ready(function() {
    var wf = frappe.web_form;

    // ---------- 1. Auto-fill Member from the logged-in user ----------
    if (!wf.get_value('member')) {
        frappe.call({
            method: 'library_management.library.web_form.library_borrow_request.library_borrow_request.get_member_for_user',
            callback: function(r) {
                if (r.message) {
                    wf.set_value('member', r.message);
                }
            }
        });
    }

    // ---------- 2. Book availability validation ----------
    wf.on('library_book', function(field, value) {
        if (!value) return;
        frappe.call({
            method: 'library_management.library.web_form.library_borrow_request.library_borrow_request.get_book_availability',
            args: { book: value },
            callback: function(r) {
                var info = r.message;
                if (!info) return;
                if (!info.published) {
                    frappe.msgprint({
                        title: __('Book Not Available'),
                        message: __("'{0}' is not published and cannot be borrowed. Please choose another book.", [info.book_name]),
                        indicator: 'orange'
                    });
                    wf.set_value('library_book', '');
                } else if (info.available_copies <= 0) {
                    frappe.msgprint({
                        title: __('Out of Stock'),
                        message: __("'{0}' is currently out of stock. Please choose another book.", [info.book_name]),
                        indicator: 'orange'
                    });
                    wf.set_value('library_book', '');
                } else {
                    frappe.show_alert({
                        message: __("'{0}' is available ({1} copy/copies in stock).", [info.book_name, info.available_copies]),
                        indicator: 'green'
                    });
                }
            }
        });
    });

    // ---------- 3. Date validation (due date cannot precede borrow date) ----------
    wf.on('due_date', function(field, value) {
        var borrow_date = wf.get_value('borrow_date');
        if (value && borrow_date && value < borrow_date) {
            frappe.msgprint({
                title: __('Invalid Due Date'),
                message: __('The due date cannot be before the borrow date. Please choose a later date.'),
                indicator: 'orange'
            });
            wf.set_value('due_date', '');
        }
    });

    // ---------- 4. Prefill book from URL if available ----------
    var urlParams = new URLSearchParams(window.location.search);
    var book = urlParams.get('book');
    if (book && !wf.get_value('library_book')) {
        wf.set_value('library_book', book);
    }
});
