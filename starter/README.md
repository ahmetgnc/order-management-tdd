# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Reflection

- I kept the order logic in `OrderTracker`, so the Flask routes only need to read requests and return responses. For example, the tracker returns `None` when an order is missing, and the route responds with 404.
- Writing the duplicate-order test first gave me a clear next step: check whether the ID exists before saving. I also checked that `save_order` was never called in that case. Using mock storage made it easy to set up a missing or existing order and see exactly what the tracker tried to save. The API tests then checked the same operations with the real storage.
- Next, I would work on input validation. Missing fields and duplicate IDs in POST requests still need proper JSON error responses. I would write tests for those cases before changing the routes.
