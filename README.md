# Library Management

Library Management System built with Frappe Framework v16.

---

# Assignment 1 — Basics Python API

This assignment demonstrates DocType Controllers, document lifecycle events, and Hooks.

## 1. Controller Lifecycle

Created a **Test Document** DocType with a Description field.

Implemented the `before_save()` lifecycle method in the DocType controller to automatically set a default description when the Description field is empty.

### Verify

Go to:

**Desk → Test Document → New**

Leave **Description** empty and save the document.

The Description will automatically become:

`Default Description`

**Code:**  
`library_management/library/doctype/test_document/test_document.py`

## 2. Document Events & Hooks

Added an `after_insert` document event in `hooks.py`.

When a new Test Document is created, the custom function is executed and displays:

`Hook executed!`

### Verify

Go to:

**Desk → Test Document → New**

Create and save a new Test Document.

Verify that:

`Hook executed!`

is displayed.

**Hook:**  
`library_management/hooks.py`

**Function:**  
`library_management/api.py`

---

# Assignment 2 — Python API: Document, Database & Query Builder

This assignment demonstrates Whitelisted APIs, Query Builder, Document API, Database API, and Client Scripts.

## 1. Whitelisted Python API

Created a Whitelisted Python method named `document_api_demo()`.

The method is called from the Desk using `frappe.call()`.

**Code:**  
`library_management/custom_module/doctype/test_document/test_document.py`

## 2. Query Builder

Used `frappe.qb` to join **Test Document** and **Test Related Document** and retrieve the required fields.

### Verify

Open a **Test Related Document** and click:

**Run Document API**

The Query Builder runs as part of the API.

## 3. Document API

Used `frappe.get_doc()` to fetch the linked Test Document, update its Description, and save it.

The Description is updated to:

`Updated using Document API`

### Verify

1. Open a **Test Related Document**.
2. Click **Run Document API**.
3. Open the linked **Test Document**.
4. Check the Description.

It should show:

`Updated using Document API`

## 4. Database API

Used `frappe.db.set_value()` to update the status of the related document.

The status changes from:

`Pending → Processed`

### Verify

Open the **Test Related Document** after clicking **Run Document API**.

The Status should be:

`Processed`

## 5. Client Script

Added a **Run Document API** button to the Test Related Document form.

The button uses `frappe.call()` to execute the Whitelisted Python method.

### Verify

Go to:

**Desk → Test Related Document**

Open a document and click:

**Run Document API**

The linked documents should be updated.

---

# Assignment 3 — Scheduled Tasks

This assignment demonstrates Frappe Scheduler Events and scheduled Python tasks.

## 1. Daily Scheduled Tasks

Added two daily scheduled tasks in `hooks.py`:

- `library_management.tasks.daily_check`
- `library_management.custom_module.tasks.daily_maintenance`

Both scheduled tasks were tested successfully.

## 2. Scheduler Status

The scheduler is enabled for the site.

### Verify

Run:

```bash
bench --site test-library.local scheduler status
```

Expected output:

```text
Scheduler is enabled for site test-library.local
```

## 3. Test Scheduled Tasks Manually

The individual scheduled methods can be triggered manually for testing.

### Daily Check

Run:

```bash
bench --site test-library.local trigger-scheduler-event library_management.tasks.daily_check
```

Expected output:

```text
Daily scheduler task executed.
```

### Daily Maintenance

Run:

```bash
bench --site test-library.local trigger-scheduler-event library_management.custom_module.tasks.daily_maintenance
```

The task executes successfully.

## Scheduler Code

**Hooks:**  
`library_management/hooks.py`

**Daily Check:**  
`library_management/tasks.py`

**Daily Maintenance:**  
`library_management/custom_module/tasks.py`

---

# Installation

You can install this app using the Bench CLI:

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app $URL_OF_THIS_REPO --branch version-16

bench --site $SITE_NAME install-app library_management
```

# License

MIT