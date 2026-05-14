Contributing
============

Thanks for considering a contribution to Raiz!

Local Development
-----------------

Clone the repository and install the project in editable mode with dev dependencies:

.. code-block:: bash

   git clone https://github.com/daleonpz/raiz.git
   cd raiz
   pip install -e ".[dev]"

The ``raiz`` command is available immediately after the editable install:

.. code-block:: bash

   raiz --help

Linting and Formatting
----------------------

.. code-block:: bash

   make lint
   make format

Testing
-------

System tests use Robot Framework:

.. code-block:: bash

   make tests

``make tests`` runs ``robot tests/system`` under the hood.
