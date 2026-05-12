# 🧰 Raiz - Simple CLI Requirements Management Tool

A CLI tool to manage, track, and trace software requirements with automated test case linking, traceability reporting, and seamless integration with Robot Framework.

> Built for developers and teams working with embedded systems, Zephyr RTOS, or other projects where traceability and coverage are crucial.

You can try Raiz using the provided [example](example/).

## 📚 Table of Contents

* [🚀 Features](#features)
* [📦 Installation](#installation)
* [✍️ Requirements Format (YAML)](#requirements-format-yaml)
* [🧪 Robot Framework Integration](#robot-framework-integration)
* [🧾 CLI Usage](#cli-usage)
  * [Add a Requirement](#add-a-requirement)
  * [Remove a Requirement](#remove-a-requirement)
  * [Trace Requirements Coverage](#trace-requirements-coverage)
  * [List Requirements](#list-requirements)
  * [Update Requirement](#update-requirement)
  * [Sync Requirements](#sync-requirements)
* [📁 Reports and Temp Files](#reports-and-temp-files)
* [🧪 Testing](#testing)
* [🏗️ Roadmap](#roadmap)
* [📄 License](#license)
* [🤝 Contributing](#contributing)

## 🚀 Features

* 📄 **Define and manage software requirements** (Functional, Non-functional, Constraints)
* 🔗 **Link test cases** (from Robot Framework) to specific requirements using tags (e.g., `REQ-001`)
* ✅ **Trace test coverage** — which requirements are tested, which are missing
* 🗃️ **SQLite-backed DB** for performance and reliability
* 🧪 **Robot Framework integration** using `output.xml`
* 📦 Installable via `pip`
* 📊 **Traceability reporting**: Console, JSON
* 🧹 Automatic renumbering of requirements
* 🧰 Modular and extensible codebase


## 📦 Installation

```bash
pip install raiz
```

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

## 🧪 Robot Framework Integration

Tests should be tagged with requirement IDs:

```robot
*** Test Cases ***
Test BLE Connection
    [Tags]    REQ-001
    Do Something
```

After executing tests (which generates `output.xml`), you can trace coverage.

## 🧾 CLI Usage

Run **raiz** from your repository

```bash
cd my_repo/
raiz <command> [options]
```

### Add a Requirement

```bash
raiz add
```

Prompts for description, type, domain.

### Remove a Requirement

```bash
raiz rm <req_number>
raiz rm 3
```

Deletes requirement `REQ-003` and renumbers all remaining ones.

### Trace Requirements Coverage

```bash
raiz trace --fmt json --output trace_report
```

* `--format`: `console`, `json`
* `--robot-output`: location of the Robot Framework output file
* `--output`: output of the report file. The extension is added automatically
* `--detail`: generates a more detailed trace report

```json
{
    "timestamp": "2025-08-08T19:16:46.837013",
    "coverage": {
        "total_requirements": 2,
        "tested_requirements": 2,
        "pass_rate": 75.0,
        "coverage_rate": 100.0
    },
    "report": {
        "REQ-001": {
            "uuid": "c567c0d4-fe18-4d9b-8a1a-2e6b128ed89f",
            "description": "Library should have add function",
            "type": "functional",
            "domain": "math",
            "linked_tests": [
                "Add Integers",
                "Fail Add Integers"
            ],
            "test_results": [
                [
                    "test_math.robot",
                    "Add Integers",
                    "PASS"
                ],
                [
                    "test_math.robot",
                    "Fail Add Integers",
                    "FAIL"
                ]
            ]
        },
        "REQ-XXX": {
           ...
        }
    },
    "detailed_report": {
        "domains": {
            "math": {
                "total_requirements": 2,
                "tested_requirements": 2,
                "pass_rate": 75.0,
                "coverage_rate": 100.0
            }
        },
        "types": {
            "functional": {
                "total_requirements": 2,
                "tested_requirements": 2,
                "pass_rate": 75.0,
                "coverage_rate": 100.0
            }
        }
    }
}
```

Options valid only for `--fmt console`

* `--domain`: Filter report by specific domain
* `--type`: Filter report by specific requirement type

```bash
raiz trace --fmt console --domain ble
raiz trace --fmt console --type functional
```

<img width="746" height="285" alt="image" src="https://github.com/user-attachments/assets/bf577a2a-1036-456f-a677-01a20cec6ee4" />


### Show Requirements

```bash
raiz show all       # Show all saved requirements
raiz show domains   # Show all unique domains found across the saved requirements
raiz show types     # Show all unique requirement types found across the saved requirements
```

<img width="745" height="111" alt="image" src="https://github.com/user-attachments/assets/a37afe18-2d23-45bb-8d51-ee0c4582cd22" />


### Update Requirement

```bash
raiz update <req_number>
raiz update 3
```

Prompts to update description/type/domain

Or directly update the `type` for requirement REQ-003

```bash
raiz update 3 --field type -value performance
```

### Sync Requirements

Requirements are stored in a temporary SQLite database. To generate a YAML file with all requirements and commit your changes, use: 

```bash
raiz sync to-yaml
git add requirements.yaml
```

If you have a `requirements.yaml` file and want to load it into the SQLite database, use:

```bash
raiz sync from-yaml
```

## Reports and Temp Files

* `.req_cache/` contains temporal files required to manage requirements
* `traceability.json` default output

## 🧪 Testing

```bash
robot tests/system
```

## 🏗️ Roadmap

* [x] Report in YAML format
* [x] Multiple output formats (Console/JSON)
* [ ] Support to [Requirements Interchange Format - ReqIF](https://de.wikipedia.org/wiki/Requirements_Interchange_Format)
* [ ] Support for the Zephyr RTOS testing framework.
* [ ] Improve documentation and create wiki.

## 📄 License

Apache License 2.0

## 🤝 Contributing

Pull requests are welcome!

### Local Development Setup

After cloning the repository, install the package in **editable mode** along with dev dependencies. This lets you run `raiz` directly and pick up any code changes without reinstalling:

```bash
git clone https://github.com/daleonpz/raiz.git
cd raiz
pip install -e ".[dev]"
```

### Running Raiz Without Installing

With an editable install (`-e`), the `raiz` command is immediately available and reflects every source change you make under `src/raiz/`. No reinstall is needed after editing the code.

```bash
raiz --help
```

### Modifying the Code

1. Edit any file under `src/raiz/`.
2. Run `raiz <command>` to exercise the changed code directly — the editable install picks up the changes automatically.

### Linting and Formatting

```bash
make lint      # ruff check . && black --check .
make format    # black .  (auto-formats the code)
```

### Running the Tests

```bash
make system_test   # runs: robot tests/system
```

Please ensure lint and tests pass before opening a pull request.
