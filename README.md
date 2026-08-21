# Library Management

Library Management System built with Frappe Framework v16.

## Assignment: Basics Python API

This assignment demonstrates document lifecycle management and safely extending DocType behavior using **Controllers** and **Hooks** in Frappe.

### Part 1 — Controller Lifecycle

A custom `Test Document` DocType was created with a `Description` field.

The generated Python controller was extended using the `before_save()` lifecycle method.

```python
class TestDocument(Document):

    def before_save(self):
        if not self.description:
            self.description = "Default Description"
```

When a `Test Document` is saved without a Description, Frappe automatically sets:

```text
Default Description
```

The generated controller structure and type annotations are managed by Frappe and were not manually modified.

### Part 2 — Safe Overrides Using Hooks

The standard Frappe behavior is extended through the application's `hooks.py` without modifying Frappe core files.

The `Test Document` DocType uses the `after_insert` document event:

```python
doc_events = {
    "Test Document": {
        "after_insert": "library_management.api.custom_logic",
    },
}
```

The corresponding custom function is defined in `library_management/api.py`:

```python
def custom_logic(doc, method):
    frappe.msgprint("Hook executed!")
```

When a new `Test Document` is created, the `after_insert` event triggers the custom function and displays:

```text
Hook executed!
```

### Concepts Demonstrated

* DocType Controller
* `before_save` lifecycle event
* `doc_events` hooks
* `after_insert` document event
* Custom Python functions
* `frappe.msgprint()`
* Extending Frappe behavior without modifying core framework files

## Installation

You can install this app using the [Bench CLI](https://github.com/frappe/bench):

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app $URL_OF_THIS_REPO --branch version-16

bench --site $SITE_NAME install-app library_management
```

## License

MIT
