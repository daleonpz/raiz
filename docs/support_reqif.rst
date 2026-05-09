Support ReqIF
=============

Raiz now supports import and export of requirements in both YAML and ReqIF formats.

CLI changes
-----------

The previous ``sync`` command has been replaced by top-level commands:

* ``raiz import``
* ``raiz export``

Both commands accept ``--format`` (or ``-f``):

* ``yaml`` (default)
* ``reqif``

Usage examples
--------------

Export YAML (default format):

.. code-block:: bash

   raiz export

Export ReqIF:

.. code-block:: bash

   raiz export --format reqif

Import YAML:

.. code-block:: bash

   raiz import --format yaml --file requirements/requirements.yaml

Import ReqIF:

.. code-block:: bash

   raiz import --format reqif --file requirements/requirements.reqif

Internal behavior
-----------------

The internal SQLite database import pipeline now accepts normalized records coming from either YAML or ReqIF.
Sequence numbers are rebuilt consistently, UUIDs are validated (or regenerated when invalid/missing), and linked tests are preserved.
