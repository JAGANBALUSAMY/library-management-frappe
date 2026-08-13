import frappe

def execute():
    # 1. Restore/Verify Default Frappe System Roles
    default_roles = ["System Manager", "Desk User", "All", "Guest"]
    for role_name in default_roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1 if role_name in ["System Manager", "Desk User"] else 0
            }).insert(ignore_permissions=True)
            print(f"Restored default role: {role_name}")

    # 2. Create Custom Roles
    custom_roles = ["Library Administrator", "Library Manager", "Librarian", "Library Member"]
    for role_name in custom_roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1 # All library roles need desk access for now
            }).insert(ignore_permissions=True)
            print(f"Created custom role: {role_name}")

    # 3. Create/Update Users with correct roles
    users_roles = {
        "admin@library.local": ["System Manager", "Desk User", "Library Administrator"],
        "manager@library.local": ["Desk User", "Library Manager"],
        "librarian@library.local": ["Desk User", "Librarian"],
        "member1@library.local": ["Desk User", "Library Member"],
        "member2@library.local": ["Desk User", "Library Member"]
    }

    for email, roles in users_roles.items():
        if not frappe.db.exists("User", email):
            user = frappe.new_doc("User")
            user.email = email
            user.first_name = email.split('@')[0].capitalize()
            user.send_welcome_email = 0
            user.insert(ignore_permissions=True)
        else:
            user = frappe.get_doc("User", email)

        # Clear existing roles and set the exact required roles
        user.roles = []
        for r in roles:
            user.append("roles", {"role": r})
        user.save(ignore_permissions=True)
        print(f"Updated roles for user {email}: {roles}")

    # 4 & 5. Remove custom permissions for generic roles on custom DocTypes
    # This ensures that only the JSON defaults (which we already fixed) apply.
    custom_doctypes = [
        "Library Book", "Library Author", "Library Category", 
        "Library Publisher", "Library Member", "Library Borrow Record", "Library Fine"
    ]
    
    # Delete any Custom DocPerm that might be overriding our JSON configuration
    frappe.db.sql("""
        DELETE FROM `tabCustom DocPerm` 
        WHERE parent IN %s
    """, (custom_doctypes,))

    print("Users, Roles, and Permissions have been successfully configured.")
