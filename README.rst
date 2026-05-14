Raiz - Simple CLI Requirements Management Tool
===============================================

Raiz is a CLI tool to manage, track, and trace software requirements with automated
test linking and traceability reporting.

Features
--------

* Traceability reports in console or JSON format.
* Robot Framework support via ``output.xml`` parsing.
* Import/export requirements in YAML and ReqIF formats.
* YAML-based requirements files that fit cleanly in Git workflows.
* SQLite-backed requirements database for fast CLI operations.

Installation
------------

.. code-block:: bash

   pip install raiz

Quick Start
-----------

.. code-block:: bash

   raiz add
   raiz rm 3
   raiz update 3
   raiz trace --fmt json --output trace_report
   raiz import --format yaml --file requirements/requirements.yaml
   raiz export --format reqif

Requirements are stored under ``requirements/`` by default, and temporary files are
written to ``.req_cache/``.

Make Targets
------------

* ``make dev`` - install the package in editable mode with dev dependencies.
* ``make lint`` - run ruff and black checks.
* ``make tests`` - run system tests with Robot Framework.
* ``make format`` - auto-format the codebase with black.
* ``make release`` - build and upload the package to PyPI.

Documentation
-------------

* ``docs/support_reqif.rst`` - ReqIF support and import/export details.
* ``docs/contributing.rst`` - how to contribute, including testing.
* ``docs/release.rst`` - release process for new versions.

License
-------

Apache License 2.0
