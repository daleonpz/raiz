# 🧰 Raiz - Simple CLI Requirements Management Tool

A CLI tool to manage, track, and trace software requirements with automated test case linking, traceability reporting, and seamless integration with Robot Framework.

> Built for developers and teams working with embedded systems, Zephyr RTOS, or other projects where traceability and coverage are crucial.

---

## 🚀 Features

- 📄 **Define and manage software requirements** (Functional, Non-functional, Constraints)
- 🔗 **Link test cases** (from Robot Framework) to specific requirements using tags (e.g., `REQ-001`)
- ✅ **Trace test coverage** — which requirements are tested, which are missing
- 🗃️ **SQLite-backed DB** for performance and reliability
- 🧪 **Robot Framework integration** using `output.xml`
- 📦 Installable via `pip`
- 📊 **Traceability reporting**: Console, CSV, JSON
- 🧹 Automatic renumbering of requirements
- 🧰 Modular and extensible codebase
- 🧪 Unit test ready

---

## 📦 Installation

```bash
pip install raiz
```

---

## ✍️ Requirements Format (YAML)

All requirements are stored in a single `requirements.yaml` file and look like:

```yaml
- id: REQ-001
  description: "The system shall support BLE communication."
  type: functional
  domain: ble
  linked_tests: []
```

IDs are renumbered automatically.

---

## 🧪 Robot Framework Integration

Tests should be tagged with requirement IDs:

```robot
*** Test Cases ***
Test BLE Connection
    [Tags]    REQ-001
    Do Something
```

After executing tests (which generates `output.xml`), you can trace coverage.

---

## 🧾 CLI Usage

Run with:

```bash
raiz <command> [options]
```

### 📌 Add a Requirement

```bash
raiz add
```

Prompts for description, type, domain.

---

### ❌ Remove a Requirement

```bash
raiz rm <req_number>
raiz rm 3
```

Deletes requirement `REQ-003` and renumbers all remaining ones.

---

### 🧬 Trace Requirements Coverage

```bash
raiz trace --fmt json --output trace_report
```

* `--format`: `console`, `json`
* `--robot-output`: location of the Robot Framework output file
* `--output`: output of the report file. The extension is added automatically
* `--detail`: generates a more detailed trace report

Options valid only for `--fmt console`

* `--domain`: Filter report by specific domain
* `--type`: Filter report by specific requirement type

```bash
raiz trace --fmt console --domain ble
raiz trace --fmt console --type functional
```

---

### 📋 List Requirements

```bash
raiz show all       # Show all saved requirements
raiz show domains   # Show all unique domains found across the saved requirements
raiz show types     # Show all unique requirement types found across the saved requirements
```

---

### 🛠️ Update Requirement

```bash
raiz update <req_number>
raiz update 3
```

Prompts to update description/type/domain

Or directly update the `type` for requirement REQ-003

```bash
raiz update 3 --field type -value performance
```

---

## 📁 Reports and Temp Files

* `.req_cache/` contains temporal files required to manage requirements
* `traceability.json` default output

---

## 🧪 Testing

```bash
robot tests/system
```

---

## 🏗️ Roadmap

* [x] Report in YAML format
* [x] Multiple output formats (Console/JSON)
* [ ] Support to [Requirements Interchange Format - ReqIF](https://de.wikipedia.org/wiki/Requirements_Interchange_Format)
* [ ] Support for the Zephyr RTOS testing framework.

---

## 📄 License

Apache License 2.0

---

## 🤝 Contributing

Pull requests welcome! Please run the linter and tests before submitting.

```

