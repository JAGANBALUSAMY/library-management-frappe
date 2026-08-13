"""
Comprehensive verification of library_management portal and website features.
Covers Phases 2-13 of the verification plan.
"""
import frappe
from frappe.utils import cint

RESULTS = []


def _add(phase, test, expected, actual, status):
    RESULTS.append({
        "phase": phase,
        "test": test,
        "expected": expected,
        "actual": actual,
        "status": "PASS" if status else "FAIL",
    })


def _log(phase, test, expected, actual, status):
    tag = "PASS" if status else "FAIL"
    print(f"  [{tag}] {test}: expected={expected}, actual={actual}")
    _add(phase, test, expected, actual, status)


def run():
    results = {}

    # Clean up any leftover temp books from previous runs
    for name in frappe.get_all("Library Book", filters={"book_name": ["like", "Temp%"]}, pluck="name"):
        frappe.delete_doc("Library Book", name, force=True)
    frappe.db.commit()

    # ================================================================
    # PHASE 2: WEB FORM
    # ================================================================
    print("\n=== PHASE 2: WEB FORM ===")
    wf = frappe.db.exists("Web Form", "library-borrow-request")
    _log("2", "Web Form exists", "library-borrow-request", wf, bool(wf))

    if wf:
        wfd = frappe.get_doc("Web Form", "library-borrow-request")
        _log("2", "Doc Type", "Library Borrow Record", wfd.doc_type, wfd.doc_type == "Library Borrow Record")
        _log("2", "Route", "borrow-book", wfd.route, wfd.route == "borrow-book")
        _log("2", "Published", True, wfd.published, bool(wfd.published))
        _log("2", "Login Required", True, wfd.login_required, bool(wfd.login_required))

        # Check fields exist in web form
        fieldnames = [f.fieldname for f in wfd.web_form_fields]
        for required_field in ["member", "library_book", "borrow_date", "due_date"]:
            _log("2", f"Field '{required_field}' in form", True, required_field in fieldnames, required_field in fieldnames)

    # ================================================================
    # PHASE 3: WEB FORM SETTINGS
    # ================================================================
    print("\n=== PHASE 3: WEB FORM SETTINGS ===")
    if wf:
        _log("3", "allow_multiple", True, wfd.allow_multiple, bool(wfd.allow_multiple))
        _log("3", "allow_edit", True, wfd.allow_edit, bool(wfd.allow_edit))
        _log("3", "allow_delete", False, wfd.allow_delete, not wfd.allow_delete)
        _log("3", "login_required", True, wfd.login_required, bool(wfd.login_required))
        _log("3", "published", True, wfd.published, bool(wfd.published))

    # ================================================================
    # PHASE 4: WEB FORM CUSTOMIZATION
    # ================================================================
    print("\n=== PHASE 4: WEB FORM CUSTOMIZATION ===")
    if wf:
        _log("4", "Has introduction_text", True, bool(wfd.introduction_text), bool(wfd.introduction_text))
        _log("4", "Has success_title", True, bool(wfd.success_title), bool(wfd.success_title))
        _log("4", "Has success_message", True, bool(wfd.success_message), bool(wfd.success_message))
        _log("4", "Has custom_css", True, bool(wfd.custom_css), bool(wfd.custom_css))

        # Check field descriptions
        field_descs = {f.fieldname: f.description for f in wfd.web_form_fields}
        _log("4", "Member has description", True, bool(field_descs.get("member")), bool(field_descs.get("member")))
        _log("4", "Library Book has description", True, bool(field_descs.get("library_book")), bool(field_descs.get("library_book")))

    # ================================================================
    # PHASE 5: SERVER-SIDE BORROW VALIDATION
    # ================================================================
    print("\n=== PHASE 5: SERVER-SIDE VALIDATION ===")

    # Test out-of-stock rejection (create a temp book with 0 copies)
    try:
        import_library_management()
        import time as _time
        ts = int(_time.time() * 1000)
        b = frappe.new_doc("Library Book")
        b.book_name = f"Temp Out Of Stock {ts}"
        b.isbn = f"999-0-000-{ts}-8"
        b.price = 0
        b.published = 1
        b.available_copies = 0
        b.insert(ignore_permissions=True)
        frappe.db.commit()

        d = frappe.new_doc("Library Borrow Record")
        d.member = frappe.db.get_value("Library Member", {}, "name")
        d.library_book = b.name
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        d.insert(ignore_permissions=True)
        frappe.db.rollback()
        _log("5", "Out-of-stock rejected", "ValidationError", "inserted", False)
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Out-of-stock rejected", "ValidationError", type(e).__name__, "out of stock" in str(e).lower() or "not enough" in str(e).lower())

    # Test unpublished book rejection (create an unpublished book, try to borrow)
    try:
        import time as _time
        ts2 = int(_time.time() * 1000) + 1
        b = frappe.new_doc("Library Book")
        b.book_name = f"Temp Unpub Test {ts2}"
        b.isbn = f"999-0-000-{ts2}-9"
        b.price = 0
        b.published = 0
        b.available_copies = 5
        b.insert(ignore_permissions=True)

        d = frappe.new_doc("Library Borrow Record")
        d.member = frappe.db.get_value("Library Member", {}, "name")
        d.library_book = b.name
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        d.insert(ignore_permissions=True)
        frappe.db.rollback()
        _log("5", "Unpublished book rejected", "ValidationError", "inserted", False)
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Unpublished book rejected", "ValidationError", type(e).__name__, "not published" in str(e).lower() or "validation" in type(e).__name__.lower())

    # Test missing required fields
    try:
        d = frappe.new_doc("Library Borrow Record")
        d.insert(ignore_permissions=True)
        frappe.db.rollback()
        _log("5", "Missing fields rejected", "ValidationError", "inserted", False)
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Missing fields rejected", "ValidationError", type(e).__name__, "validation" in type(e).__name__.lower())

    # Test cross-member manipulation
    try:
        d = frappe.new_doc("Library Borrow Record")
        d.member = "LIB-MEM-00002"  # member2
        d.library_book = "Foundation"
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        # Login as member1
        frappe.set_user("member1@library.local")
        d.insert(ignore_permissions=True)
        frappe.db.rollback()
        _log("5", "Cross-member manipulation rejected", "ValidationError", "inserted", False)
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Cross-member manipulation rejected", "ValidationError", type(e).__name__, "validation" in type(e).__name__.lower() or "own" in str(e).lower())
    finally:
        frappe.set_user("Administrator")

    # Test valid submission
    try:
        d = frappe.new_doc("Library Borrow Record")
        d.member = frappe.db.get_value("Library Member", {"email": "member1@library.local"}, "name")
        d.library_book = "Foundation"
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        d.insert(ignore_permissions=True)
        status = d.status
        frappe.db.rollback()
        _log("5", "Valid submission succeeds", "Pending", status, status == "Pending")
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Valid submission succeeds", "no error", type(e).__name__, False)

    # Test status transition: member cannot issue
    try:
        d = frappe.new_doc("Library Borrow Record")
        d.member = frappe.db.get_value("Library Member", {"email": "member1@library.local"}, "name")
        d.library_book = "Foundation"
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        d.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.set_user("member1@library.local")
        d2 = frappe.get_doc("Library Borrow Record", d.name)
        d2.status = "Issued"
        d2.save(ignore_permissions=True)
        frappe.db.rollback()
        _log("5", "Member cannot issue book", "ValidationError", "saved", False)
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Member cannot issue book", "ValidationError", type(e).__name__, "validation" in type(e).__name__.lower() or "librarian" in str(e).lower())
    finally:
        frappe.set_user("Administrator")

    # Test librarian can issue
    try:
        d = frappe.new_doc("Library Borrow Record")
        d.member = frappe.db.get_value("Library Member", {"email": "member1@library.local"}, "name")
        d.library_book = "Foundation"
        d.borrow_date = "2026-08-11"
        d.due_date = "2026-08-25"
        d.insert(ignore_permissions=True)
        frappe.db.commit()

        d3 = frappe.get_doc("Library Borrow Record", d.name)
        d3.status = "Issued"
        d3.save(ignore_permissions=True)
        frappe.db.commit()
        final_status = frappe.db.get_value("Library Borrow Record", d.name, "status")
        frappe.db.rollback()
        _log("5", "Librarian can issue book", "Issued", final_status, final_status == "Issued")
    except Exception as e:
        frappe.db.rollback()
        _log("5", "Librarian can issue book", "Issued", type(e).__name__, False)

    # ================================================================
    # PHASE 6 & 7: PORTAL ROLES
    # ================================================================
    print("\n=== PHASE 6-7: PORTAL ROLES ===")

    # Check librarian has correct roles
    librarian_roles = frappe.get_roles("librarian@library.local")
    _log("6-7", "Librarian user has Librarian role", True, "Librarian" in librarian_roles, "Librarian" in librarian_roles)

    # Check member1 has Library Member role
    member1_roles = frappe.get_roles("member1@library.local")
    _log("6-7", "Member1 has Library Member role", True, "Library Member" in member1_roles, "Library Member" in member1_roles)

    # Check manager has Library Manager role
    manager_roles = frappe.get_roles("manager@library.local")
    _log("6-7", "Manager has Library Manager role", True, "Library Manager" in manager_roles, "Library Manager" in manager_roles)

    # Check admin has Library Administrator + System Manager
    admin_roles = frappe.get_roles("admin@library.local")
    _log("6-7", "Admin has Library Administrator role", True, "Library Administrator" in admin_roles, "Library Administrator" in admin_roles)
    _log("6-7", "Admin has System Manager role", True, "System Manager" in admin_roles, "System Manager" in admin_roles)

    # ================================================================
    # PHASE 8: CONTEXT PROCESSOR
    # ================================================================
    print("\n=== PHASE 8: CONTEXT PROCESSOR ===")
    from library_management.utils.context_processors import library_context

    ctx = frappe._dict()
    library_context(ctx)
    _log("8", "library_name set", "Frappe Library", ctx.get("library_name"), ctx.get("library_name") == "Frappe Library")
    published_count = frappe.db.count("Library Book", {"published": 1, "available_copies": (">", 0)})
    _log("8", "available_book_count from DB", published_count, ctx.get("available_book_count"), ctx.get("available_book_count") == published_count)
    _log("8", "count matches DB query", True, ctx.get("available_book_count") == published_count, ctx.get("available_book_count") == published_count)

    # ================================================================
    # PHASE 9 & 10: WEBSITE GENERATORS
    # ================================================================
    print("\n=== PHASE 9-10: WEBSITE GENERATORS ===")
    books = frappe.get_all("Library Book", fields=["name", "route", "published"])
    meta = frappe.get_meta("Library Book")
    for b in books:
        has_route = bool(b.route)
        _log("9-10", f"Book '{b.name}' has route", True, b.route, has_route)
    _log("9-10", "DocType has_web_view", True, 1, meta.has_web_view)

    # ================================================================
    # PHASE 11: REDIRECT
    # ================================================================
    print("\n=== PHASE 11: REDIRECT ===")
    hooks = frappe.get_hooks("website_redirects")
    redirect_found = any(r.get("source") == "/library-home" and r.get("target") == "/library" for r in hooks)
    _log("11", "Redirect /library-home -> /library configured", True, redirect_found, redirect_found)

    # ================================================================
    # PHASE 12: SECURITY
    # ================================================================
    print("\n=== PHASE 12: SECURITY ===")

    # Check permission hooks registered
    pqc = frappe.get_hooks("permission_query_conditions", {})
    _log("12", "permission_query_conditions for Borrow Record", True, "Library Borrow Record" in pqc, "Library Borrow Record" in pqc)

    hp = frappe.get_hooks("has_permission", {})
    _log("12", "has_permission for Borrow Record", True, "Library Borrow Record" in hp, "Library Borrow Record" in hp)

    # Test get_permission_query_conditions
    conds_member = frappe.get_attr("library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions")("member1@library.local")
    _log("12", "Member query condition filters", "member = ...", conds_member[:7] if conds_member else "none", conds_member.startswith("member =") if conds_member else False)

    conds_librarian = frappe.get_attr("library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions")("admin@library.local")
    _log("12", "Librarian query condition empty (all rows)", "", conds_librarian, conds_librarian == "")

    conds_guest = frappe.get_attr("library_management.library.doctype.library_borrow_record.library_borrow_record.get_permission_query_conditions")("Guest")
    _log("12", "Guest query condition denied", "1=0", conds_guest, conds_guest == "1=0")

    # ================================================================
    # PHASE 13: REGRESSION
    # ================================================================
    print("\n=== PHASE 13: REGRESSION ===")

    # Library Book CRUD
    try:
        b = frappe.get_doc("Library Book", "Foundation")
        _log("13", "Library Book read", "Foundation", b.name, b.name == "Foundation")
    except Exception as e:
        _log("13", "Library Book read", "Foundation", str(e)[:50], False)

    # Library Borrow Record exists
    count = frappe.db.count("Library Borrow Record")
    _log("13", "Library Borrow Record table exists", True, count >= 0, count >= 0)

    # Library Member exists
    member_count = frappe.db.count("Library Member")
    _log("13", "Library Member table exists", True, member_count >= 0, member_count >= 0)

    # Hooks loaded
    _log("13", "website_generators hook loaded", True, "Library Book" in frappe.get_hooks("website_generators"), "Library Book" in frappe.get_hooks("website_generators"))
    _log("13", "website_redirects hook loaded", True, len(frappe.get_hooks("website_redirects")) > 0, len(frappe.get_hooks("website_redirects")) > 0)
    _log("13", "update_website_context hook loaded", True, bool(frappe.get_hooks("update_website_context")), bool(frappe.get_hooks("update_website_context")))
    _log("13", "doc_events hook loaded", True, bool(frappe.get_hooks("doc_events")), bool(frappe.get_hooks("doc_events")))
    _log("13", "scheduler_events hook loaded", True, bool(frappe.get_hooks("scheduler_events")), bool(frappe.get_hooks("scheduler_events")))

    # Web Form exists in DB
    _log("13", "Web Form exists in DB", True, bool(frappe.db.exists("Web Form", "library-borrow-request")), bool(frappe.db.exists("Web Form", "library-borrow-request")))

    # Print format template exists
    import os
    app_path = os.path.join(frappe.get_app_path("library_management"), "..")
    tpl = os.path.exists(os.path.join(app_path, "library_management", "templates", "borrow_receipt.html"))
    _log("13", "Print format template exists", True, tpl, tpl)

    # Public CSS exists
    css = os.path.exists(os.path.join(app_path, "library_management", "public", "css", "library.css"))
    _log("13", "Public CSS exists", True, css, css)

    # www pages exist
    for page in ["library.html", "books.html", "borrow-history.html"]:
        exists = os.path.exists(os.path.join(app_path, "library_management", "www", page))
        _log("13", f"www/{page} exists", True, exists, exists)

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 60)
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    print(f"TOTAL: {total} | PASS: {passed} | FAIL: {failed}")

    if failed:
        print("\nFAILED TESTS:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"  Phase {r['phase']}: {r['test']}")
                print(f"    Expected: {r['expected']}")
                print(f"    Actual: {r['actual']}")

    return RESULTS


def import_library_management():
    """Ensure library_management module is importable."""
    import importlib
    try:
        importlib.import_module("library_management")
    except ImportError:
        pass
