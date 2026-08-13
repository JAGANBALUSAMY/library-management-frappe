import frappe, json

def run():
    print("=== USERS ===")
    users = frappe.get_all("User", filters={"name": ["not in", ["Guest"]]}, fields=["name"])
    for u in users:
        user = frappe.get_doc("User", u.name)
        roles = [r.role for r in user.roles]
        print(f"{u.name}: {roles}")

    print("\n=== LIBRARY BOOKS ===")
    books = frappe.get_all("Library Book", fields=["name", "book_name", "available_copies", "published", "route"])
    for b in books:
        print(dict(b))

    print("\n=== LIBRARY MEMBERS ===")
    members = frappe.get_all("Library Member", fields=["name", "member_name", "email"])
    for m in members:
        print(dict(m))

    print("\n=== BORROW RECORDS ===")
    recs = frappe.get_all("Library Borrow Record", fields=["name", "member", "library_book", "status"])
    for r in recs:
        print(dict(r))

    print("\n=== WEB FORM ===")
    if frappe.db.exists("Web Form", "library-borrow-request"):
        wf = frappe.get_doc("Web Form", "library-borrow-request")
        print(json.dumps(wf.as_dict(), indent=1, default=str))
    else:
        print("NOT FOUND")

    print("\n=== DOCPERM Library Borrow Record ===")
    perms = frappe.get_all("DocPerm", filters={"parent": "Library Borrow Record"}, fields=["role", "read", "write", "create", "delete", "if_owner"])
    for p in perms:
        print(dict(p))

if __name__ == "__main__":
    run()
