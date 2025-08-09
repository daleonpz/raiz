# Example / Tutorial

This example demonstrates how to use **Raiz** for requirements management, test linking, and traceability.

## Example Project Structure

```bash
$ tree -L 2
.
├── Makefile
├── math.c
├── math.h
├── README.md
├── requirements
│   └── requirements.yaml
└── robot
    ├── MathLibrary.py
    ├── test_math.robot
    └── test_multiplication.robot
```

**What’s in here?**

* **`Makefile`** – builds the example and runs Robot Framework tests.
* **`math.c`, `math.h`** – example source code.
* **`requirements/requirements.yaml`** – requirements file (created automatically on first run).
* **`robot/`** – Robot Framework tests and library.

## Step 1 – Build and Run Tests

```bash
cd example
make
make robot
```

Some tests will fail — that’s intentional for demonstration purposes.

## Step 2 – Import Requirements into Raiz

```bash
$ raiz sync from-yaml
```

After running, new files and folders appear:

```bash
$ tree -L 2
.
├── .req_cache
│   └── requirements.db
├── build
│   └── libmath.so
├── log.html
├── output.xml
├── report.html
├── requirements
│   └── requirements.yaml
└── robot
    ├── MathLibrary.py
    ├── test_math.robot
    └── test_multiplication.robot
```

**New folders explained:**

* `.req_cache/` – Raiz cache (requirements database).
* `build/` – compiled library.
* `log.html`, `output.xml`, `report.html` – Robot Framework logs and reports.

## Step 3 – List Requirements

```bash
$ raiz show all
```

Example output:

```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ REQ-ID  ┃ Description            ┃ Type           ┃ Domain  ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ REQ-001 │ requ 002               │ constraint     │ logging │
│ REQ-002 │ description for 002    │ non-functional │ ble     │
│ REQ-003 │ another example desc   │ functional     │ wlan    │
│ REQ-004 │ extra req              │ functional     │ logging │
│ REQ-005 │ new example            │ constraint     │ ble     │
└─────────┴────────────────────────┴────────────────┴─────────┘
```

## Step 4 – Update a Requirement

Interactive update:

```bash
$ raiz update 1
Updating REQ-001 interactively. Leave blank to keep existing values.
Domain [logging]:
Type [constraint]:
Description [requ 002]: Raiz should update a requirement
REQ-001 updated successfully!
```

Verify:

```bash
$ raiz show all
```

## Step 5 – Remove a Requirement

```bash
$ raiz rm 5
REQ-005 removed
```

## Step 6 – Generate a Traceability Report

```bash
$ raiz trace --fmt console
```

Example console report:

```
Coverage Summary
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Total Requirements ┃ Tested Requirements ┃ Pass Rate ┃ Coverage ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ 4                  │ 3                   │ 83.33%    │ 75.0%    │
└────────────────────┴─────────────────────┴───────────┴──────────┘

Requirement Traceability Report
┏━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ REQ-ID  ┃ Status     ┃ suite                     ┃ linked_test             ┃
┡━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ REQ-001 │ PASS       │ test_math.robot           │ Add Integers            │
│ REQ-001 │ FAIL       │ test_math.robot           │ Fail Add Integers       │
│ REQ-002 │ PASS       │ test_math.robot           │ Multiply Boundaries Low │
│ REQ-002 │ PASS       │ test_multiplication.robot │ Multiply Integers       │
│ REQ-003 │ PASS       │ test_math.robot           │ Multiply Boundaries     │
│ REQ-003 │ PASS       │ test_math.robot           │ Multiply Boundaries Low │
│ REQ-004 │ NOT TESTED │ -                         │ -                       │
└─────────┴────────────┴───────────────────────────┴─────────────────────────┘
```

## Step 7 – Export Requirements Back to YAML

```bash
$ raiz sync to-yaml
Using provided YAML file: requirements/requirements.yaml
Exported 4 requirements to requirements/requirements.yaml
```

Check the file:

```bash
$ cat requirements/requirements.yaml
# or
$ git diff requirements/requirements.yaml
```
