Raiz - Simple CLI Requirements Management Tool
==============================================

Raiz is a CLI tool to manage, track, and trace software requirements with
automated test linking and traceability reporting.

.. image:: https://github.com/user-attachments/assets/a37afe18-2d23-45bb-8d51-ee0c4582cd22
   :alt: Show requirements output
   :width: 745px

Contents
--------

- Features_
- Installation_
- `Quick Start <#quick-start>`_
- `Robot Framework Integration <#robot-framework-integration>`_
- Documentation_
- License_

Features
--------

* Traceability reports in console or JSON format.
* Robot Framework support via ``output.xml`` parsing.
* Import/export requirements in YAML and ReqIF formats.
* YAML-based requirements files that fit cleanly in Git workflows.
* SQLite-backed requirements database for fast CLI operations.

.. image:: https://github.com/user-attachments/assets/bf577a2a-1036-456f-a677-01a20cec6ee4
   :alt: Traceability console report
   :width: 746px

Installation
------------

.. code-block:: bash

   pip install raiz

.. _quick-start:

Quick Start
-----------

Download the `example
<https://github.com/daleonpz/raiz/tree/main/example>`_.

.. code-block:: bash

   cd example
   make robot
   raiz import --format yaml --file requirements/requirements.yaml
   raiz show all
   raiz add
   raiz update 3
   raiz rm 5
   raiz trace --fmt json --output trace_report
   raiz export --format reqif
   raiz export --format yaml

Requirements are stored under ``requirements/`` by default, and temporary
files are written to ``.req_cache/``.

.. _robot-framework-integration:

Robot Framework Integration
---------------------------

Tests should be tagged with requirement IDs:

.. code-block:: robotframework

   *** Test Cases ***
   Test BLE Connection
       [Tags]    REQ-001
       Do Something

After executing tests (which generates ``output.xml``), you can trace
coverage.

Documentation
-------------

* ``docs/support_reqif.rst`` - ReqIF support and import/export details.
* ``docs/contributing.rst`` - How to contribute, including testing.
* ``docs/release.rst`` - Release process for new versions.

License
-------

Apache License 2.0
