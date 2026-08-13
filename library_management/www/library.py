import frappe


def get_context(context):

    context.no_cache = 1

    books = frappe.get_all(
        "Library Book",
        filters={
            "published": 1
        },
        fields=[
            "name",
            "book_name",
            "author",
            "available_copies",
            "price",
            "route",
            "library_total_borrows",
            "library_last_borrowed",
        ],
        order_by="book_name asc",
    )

    _resolve_books(books)

    context.books = books

    return context


def _resolve_books(books):

    for book in books:

        # -----------------------------------------------------
        # Display name
        # -----------------------------------------------------

        book.display_name = (
            book.book_name or ""
        ).replace("-", " ").replace("_", " ").title()


        # -----------------------------------------------------
        # Author name
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
        # Price
        # -----------------------------------------------------

        book.price_display = _format_price(
            book.price
        )


        # -----------------------------------------------------
        # Last borrowed
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
        # Available copies
        # -----------------------------------------------------

        book.available_copies = (
            book.available_copies or 0
        )


def _format_price(price):

    if price is None:
        return ""

    if price == int(price):
        return f"₹{int(price)}"

    return f"₹{price}"