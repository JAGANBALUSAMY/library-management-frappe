import frappe


def get_context(context):

    context.no_cache = 1

    books = frappe.db.get_all(
        "Library Book",
        filters={
            "published": 1
        },
        fields=[
            "name",
            "book_name",
            "author",
            "isbn",
            "category",
            "available_copies",
            "price",
            "route",
            "library_total_borrows",
            "library_last_borrowed",
        ],
        order_by="book_name asc",
    )


    for book in books:

        # -----------------------------------------------------
        # Display Name
        # -----------------------------------------------------

        book.display_name = (
            book.book_name or ""
        ).replace("-", " ").replace("_", " ").title()


        # -----------------------------------------------------
        # Author
        # -----------------------------------------------------

        if book.author:

            book.author_name = (
                frappe.db.get_value(
                    "Library Author",
                    book.author,
                    "author_name",
                )
                or book.author
            )

        else:

            book.author_name = "Unknown"


        # -----------------------------------------------------
        # Category
        # -----------------------------------------------------

        if book.category:

            book.category_name = (
                frappe.db.get_value(
                    "Library Category",
                    book.category,
                    "category_name",
                )
                or book.category
            )

        else:

            book.category_name = "Uncategorized"


        # -----------------------------------------------------
        # Price
        # -----------------------------------------------------

        if book.price is not None:

            if book.price == int(book.price):

                book.price_display = (
                    f"₹{int(book.price)}"
                )

            else:

                book.price_display = (
                    f"₹{book.price}"
                )

        else:

            book.price_display = ""


        # -----------------------------------------------------
        # Last Borrowed
        # -----------------------------------------------------

        if book.library_last_borrowed:

            book.last_borrowed_display = (
                book.library_last_borrowed.strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

        else:

            book.last_borrowed_display = "Never"


        # -----------------------------------------------------
        # Available Copies
        # -----------------------------------------------------

        book.available_copies = (
            book.available_copies or 0
        )


    context.books = books

    return context