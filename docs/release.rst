Release Process
===============

Raiz uses ``pyproject.toml`` with ``setuptools`` to build and publish releases.

Prerequisites
-------------

* Python build tooling: ``python -m pip install --upgrade build twine``
* PyPI credentials configured via ``~/.pypirc`` or ``TWINE_USERNAME``/``TWINE_PASSWORD``

Steps
-----

1. Update the version in ``pyproject.toml``.
2. Run the quality checks:

   .. code-block:: bash

      make lint
      make tests

3. Build and upload the package:

   .. code-block:: bash

      make release

   (Equivalent to ``python -m build`` and ``python -m twine upload dist/*``.)
4. Tag and push the release:

   .. code-block:: bash

      git tag vX.Y.Z
      git push origin vX.Y.Z
