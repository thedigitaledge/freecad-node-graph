Code Quality & Sphinx Documentation Integration
================================================

The **FreeCAD NodeGraph** workbench maintains strict testing, code quality, and documentation standards to ensure reliability and maintainability.

Building Sphinx Documentation
-----------------------------

Documentation is generated using Sphinx and configured for Read the Docs.

Installation
~~~~~~~~~~~~

Install documentation dependencies specified in ``pyproject.toml``:

.. code-block:: bash

   pip install .[docs]

Building HTML Docs
~~~~~~~~~~~~~~~~~~

Generate HTML documentation from Sphinx sources:

.. code-block:: bash

   sphinx-build -b html docs docs/_build/html

The generated HTML documentation will be placed in ``docs/_build/html/index.html``.

Automated Test Suite
--------------------

The test suite is built on `pytest` and encompasses unit, integration, and behavior-driven automation tests.

Running Tests Headlessly
~~~~~~~~~~~~~~~~~~~~~~~~

Run all tests headlessly using PySide/Qt offscreen mode:

.. code-block:: bash

   PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest

Offscreen execution is configured automatically via ``tests/conftest.py``.

Behavior-Driven Automation (pytest-bdd)
----------------------------------------

User interface workflows are specified in Gherkin feature files (``tests/features/node_graph_ui.feature``) and implemented using ``pytest-bdd`` (``tests/step_defs/test_node_graph_ui_steps.py``).

Covered Scenarios
~~~~~~~~~~~~~~~~~
- **Node Library Additions:** Double-clicking nodes in the Task View palette to populate the active MDI canvas.
- **Socket Wiring:** Connecting output and input sockets to form graph DAG relationships.
- **Property Value Editing:** Manual entry and inline type validation for Float, Integer, String, Boolean, Vector, and Placement nodes.
- **Node Deletion:** Removing selected canvas nodes via context menu or ``Del``/``Backspace`` key shortcuts.
- **Undo / Redo:** Rolling back and restoring visual graph modifications seamlessly.

Integrating Code Coverage with Documentation
--------------------------------------------

Code coverage is monitored automatically during test runs via ``pytest-cov``.

Generating Coverage Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run pytest with HTML coverage report generation:

.. code-block:: bash

   pytest --cov=freecad_nodegraph --cov-report=term-missing --cov-report=html:docs/_build/html/coverage

Integrating Coverage HTML with Sphinx Build
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running ``pytest`` with ``--cov-report=html:docs/_build/html/coverage``, the code coverage HTML report is placed directly inside Sphinx's output build directory, making interactive coverage reports accessible alongside Sphinx API documentation.

Configuration in ``pyproject.toml``:

.. code-block:: toml

   [tool.pytest.ini_options]
   addopts = "--cov=freecad_nodegraph --cov-report=term-missing"

   [tool.coverage.run]
   source = ["freecad_nodegraph"]

   [tool.coverage.report]
   show_missing = true

Code Quality & Static Analysis
------------------------------

Automated quality tools are configured in ``pyproject.toml`` under ``[project.optional-dependencies.dev]``:

- **Flake8:** Enforces PEP 8 syntax, unused imports, and line length rules.
- **Black:** Automated code formatting for consistent structure.
- **Mypy:** Static type checking for type annotations.

Run Quality Checks
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check PEP 8 compliance
   flake8 freecad_nodegraph tests

   # Check formatting
   black --check freecad_nodegraph tests

   # Check static types
   mypy freecad_nodegraph
