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

# Assignment 5 — Python API Utilities

This assignment demonstrates secure data fetching, optimized database access, server time, and REST API handling.

## 1. Whitelisted Python API

Created a Whitelisted Python method named `get_recent_todos()`.

The method is available through the Frappe REST API.

**Code:**

`library_management/custom_module/api.py`

## 2. Secure ToDo Fetching

Used `frappe.get_list()` to fetch the 5 most recently created **ToDo** records.

Only the required fields are fetched:

- `name`

- `description`

- `owner`

The records are ordered by creation time, with the newest records returned first.

## 3. Owner Email

Used `frappe.db.get_value()` to fetch the email address of each ToDo owner's **User** record.

The email is included with each returned record.

## 4. Server Timestamp

Used `frappe.utils.now()` to get the current server timestamp.

The timestamp is included in the API response.

## 5. REST API Verification

The endpoint was tested directly through the browser while logged in.

Open:

```text

http://test-library.local:8000/api/method/library_management.custom_module.api.get_recent_todos

```

The response contains:

- Current timestamp

- Recently created ToDo records

- ToDo name

- Description

- Owner

- Owner email

Example response:

```json

{

"message": {

    "timestamp": "2026-08-21 15:36:57.029074",

    "records": [

        {

            "name": "o2nfgsf7oh",

            "description": "\<div class=\\"ql-editor read-mode\\">\<p>Test ToDo 3\</p>\</div>",

            "owner": "admin\@gmail.com",

            "email": "admin\@gmail.com"

        }

    ]

}

}

```

---

---

# Assignment 6 — JavaScript Frappe Dialog & Router

Implemented a JavaScript dialog using `frappe.ui.Dialog` to collect a **First Name**.

The entered value is passed through `frappe.route_options` and used with `frappe.new_doc('Contact')` to pre-fill the **First Name** field in a new Contact document.

### Verify

Open the **Desk browser console** and run the JavaScript implementation.

Enter a First Name and click **Create Contact**.

Verify that:

**Desk → Contact → New**

opens with the entered First Name automatically populated.

---

# Assignment 7 — JavaScript Frappe Call

Implemented a frontend dialog for entering a **Task Subject** and connected it to a whitelisted Python method using `frappe.call()`.

The backend method uses `frappe.new_doc('Task')` to create the Task and returns the created document name.

The frontend displays the result using `frappe.msgprint()` with a green success indicator.

### Verify

Open the **Desk browser console** and run the JavaScript implementation.

Enter a Task Subject and click **Create Task**.

The `frappe.call()` request reaches the backend method.

**Note:** Task creation cannot currently be completed on this site because the **Task DocType is not available**. The frontend dialog and backend API call are implemented and tested up to the document creation step.

---

# Assignment 8 — Custom Bench CLI Command

Implemented a custom Bench CLI command in the Library Management app.

Created:

`library_management/commands.py`

The command uses Click and is registered through the app's `commands` list.

### Verify

From the Bench directory, run:

```bash

bench --help

```

Verify that the custom command appears in the available Bench commands.

Then run:

```bash

bench hello-custom

```

Expected output:

```text

Hello from the custom Bench CLI!

```

---

# Assignment 9 — Bench CLI Multitenancy

Configured a new site using **port-based multitenancy**.

Implemented:

* Disabled DNS-based multitenancy.

* Created the `testsite.local` site.

* Assigned port `82` to the site.

* Added the custom domain `internal.testsite.local`.

* Regenerated the Nginx configuration.

* Reloaded Nginx.

### Verify

The site configuration can be checked at:

`sites/testsite.local/site_config.json`

The configuration contains:

```json

"nginx_port": 82,

"domains": [

"internal.testsite.local"

]

```

The site can be accessed using:

```text

http://internal.testsite.local:82

```

---



**# Assignment 10 — Library Book Print Report

Implemented a custom Script Report with a custom HTML print format for the Library Book DocType.

1. Script Report

Created Library Book Print Report.

Verify:

Desk → Report → Library Book Print Report

The report displays:

Book Name

Author

Issue Date

Book Price

Files:

library_management/library/report/library_book_print_report/library_book_print_report.py

library_management/library/report/library_book_print_report/library_book_print_report.js

library_management/library/report/library_book_print_report/library_book_print_report.json

2. Report Print Format

Created the report HTML print format:

library_management/library/report/library_book_print_report/library_book_print_report.html

The template uses Frappe micro-templating with:

<% %> loop syntax

Double-quoted JavaScript strings

Bootstrap 3 table classes

data array values

filters.author

Date formatting

Currency formatting

Verify:

Desk → Report → Library Book Print Report → Actions → Print → Submit

The generated print report displays the Library Book data.

3. Author Filter

Added an Author filter to the report.

The filter supports case-insensitive partial matching.

Verify:

Desk → Report → Library Book Print Report

Enter values such as:

John

john

Smith

The matching author records are displayed.

Assignment 11 — Jinja & Report Print Formats

Implemented a Jinja Print Format for the Library Book DocType and a micro-template Report Print Format.

1. Jinja Print Format

Created Library Book Jinja Print Format.

Configured it as:

Print Format For: DocType

DocType: Library Book

Print Format Type: Jinja

Custom Format: Enabled

Standard: Yes

The format uses Jinja templating and Bootstrap 3 classes to display:

Book Name

Author

Issue Date

Book Price

File:

library_management/library/print_format/library_book_jinja_print_format/library_book_jinja_print_format.json

Verify:

Desk → Library Book → open a record → Print → select Library Book Jinja Print Format

2. Report Print Format

Updated Library Book Print Report with a custom HTML print format using Frappe's JavaScript micro-templating.

The template:

Uses <% %> to loop through data

Uses strictly double quotes in JavaScript logic

Uses Bootstrap 3 table classes

Displays the selected author filter

Formats Issue Date

Formats Book Price

File:

library_management/library/report/library_book_print_report/library_book_print_report.html

Verify:

Desk → Report → Library Book Print Report → Actions → Print → Submit

The print output displays the report data and the selected Author filter.

Installation**

You can install this app using the Bench CLI:

```bash

cd $PATH_TO_YOUR_BENCH

bench get-app $URL_OF_THIS_REPO --branch version-16

bench --site $SITE_NAME install-app library_management

```

# License

MIT