// --- TASK 3: Overriding Link Query ---
// Show only published + available books in the library_book link field
frappe.ui.form.on('Library Borrow Record', {
    library_book: function(frm) {
        // Triggered when a book is selected — fetch author via fetch_from
    },

    refresh: function(frm) {
        // TASK 3: Filter link to show only published + available books
        frm.set_query('library_book', function() {
            return {
                filters: {
                    published: 1,
                    available_copies: ['>', 0]
                }
            };
        });
    }
});
