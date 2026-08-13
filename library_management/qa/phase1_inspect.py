import frappe

def run():
    # Web Forms
    wfs = frappe.get_all("Web Form", fields=["name","doc_type","route","published","login_required","allow_multiple","allow_edit","allow_delete"])
    print("=== Web Forms ===")
    for w in wfs:
        print(dict(w))

    # Library roles
    roles = frappe.get_all("Role", filters={"role_name":["like","%Library%"]}, pluck="role_name")
    print("\n=== Library Roles ===", roles)

    # Users with roles
    users = frappe.get_all("User", fields=["name","email","user_type"], filters={"name":["not in",["Guest","Administrator"]]})
    print("\n=== Users ===")
    for u in users:
        user_roles = frappe.get_roles(u.name)
        lib_roles = [r for r in user_roles if "library" in r.lower() or r == "System Manager"]
        print(f"  {u.name} | roles: {lib_roles}")

    # Hooks
    hooks = frappe.get_hooks()
    print("\n=== website_redirects ===")
    for r in hooks.get("website_redirects", []):
        print(f"  {r.get('source')} -> {r.get('target')}")
    print("=== website_generators ===", hooks.get("website_generators", []))

    # Library Book settings
    meta = frappe.get_meta("Library Book")
    print("\n=== Library Book meta ===")
    print(f"  has_web_view: {meta.has_web_view}")
    print(f"  is_published_field: {meta.is_published_field}")

    # Website Settings
    ws = frappe.get_doc("Website Settings")
    print("\n=== Website Settings ===")
    print(f"  home_page: {ws.home_page}")
    print(f"  top_bar_items: {[(i.label, i.url) for i in ws.top_bar_items]}")

    # Library Books
    books = frappe.get_all("Library Book", fields=["name","published","route"])
    print("\n=== Library Books ===")
    for b in books:
        print(f"  {b.name} | published={b.published} | route={b.route}")

    # Context processor check
    print("\n=== Context Processor Hook ===")
    print(f"  update_website_context: {hooks.get('update_website_context', [])}")

    # Permission hooks
    print("\n=== Permission Hooks ===")
    print(f"  permission_query_conditions: {list(hooks.get('permission_query_conditions', {}).keys())}")
    print(f"  has_permission: {list(hooks.get('has_permission', {}).keys())}")

    print("\n=== INSPECTION COMPLETE ===")
