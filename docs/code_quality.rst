Code Quality & Automated Testing
================================

The **FreeCAD NodeGraph** workbench maintains strict testing and code quality standards to ensure reliability across FreeCAD versions and standalone environments.

Automated Test Suite
--------------------

The test suite is built on `pytest` and encompasses unit, integration, and behavior-driven automation tests.

Running Tests
~~~~~~~~~~~~~

Run all tests headlessly using the pytest command:

.. code-block:: bash

   PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest

All tests execute in offscreen mode using Qt's offscreen platform plugin, configured automatically via ``tests/conftest.py``.

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

Code Coverage (pytest-cov)
--------------------------

Code coverage is monitored automatically during test runs via ``pytest-cov``.

Run test coverage report:

.. code-block:: bash

   pytest --cov=freecad_nodegraph --cov-report=term-missing

Configuration in ``pyproject.toml``:

.. code-block:: toml

   [tool.pytest.ini_options]
   addopts = "--cov=freecad_nodegraph --cov-report=term-missing"

   [tool.coverage.run]
   source = ["freecad_nodegraph"]

Code Style & Linting
--------------------

The codebase follows PEP 8 standards with the following automated tools configured in ``pyproject.toml``:

- **Flake8:** Linter for syntax, imports, and style rules.
- **Black:** Code formatter for consistent code layout.
- **Mypy:** Static type checker for Python type annotations.

Run linter checks:

.. code-block:: bash

   flake8 freecad_nodegraph tests
