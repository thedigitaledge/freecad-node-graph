Code Quality & Sphinx Documentation Integration
================================================

The **FreeCAD NodeGraph** workbench maintains strict testing, code quality, and documentation standards to ensure reliability and maintainability.

Building Sphinx Documentation (Primary Creation Method)
-------------------------------------------------------

Local offline generation using Sphinx is the **primary method** for creating and building documentation in this project.

Installation
~~~~~~~~~~~~

Install documentation dependencies specified in ``pyproject.toml``:

.. code-block:: bash

   pip install .[docs]

Building Offline HTML Docs
~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate standalone HTML documentation locally without any internet or network dependencies:

.. code-block:: bash

   sphinx-build -b html docs docs/_build/html

Source Code Links (sphinx.ext.viewcode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Sphinx ``sphinx.ext.viewcode`` extension is enabled in ``docs/conf.py``. During documentation compilation, Sphinx scans the Python source modules in ``freecad_nodegraph/`` and builds syntax-highlighted HTML source view pages under ``docs/_build/html/_modules/``. Each API element documented in the Sphinx API reference contains a **[source]** hyperlink that points directly to its corresponding definition in the source view.

Serve and View Local Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Serve built HTML documentation using Python's built-in HTTP server:

.. code-block:: bash

   python3 -m http.server -d docs/_build/html

Navigate to ``http://localhost:8000`` in your browser to view the offline documentation.

Automated Test Suite & Speed Profiling
---------------------------------------

The test suite is built on `pytest` and encompasses unit, integration, and behavior-driven automation tests with automatic execution duration profiling.

Running Tests Headlessly with Speed Profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run all tests headlessly in PySide/Qt offscreen mode while profiling test durations:

.. code-block:: bash

   PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest

The ``--durations=0`` flag is configured in ``pyproject.toml`` to automatically profile and print execution timings for all test calls, setups, and teardowns across unit, integration, and BDD scenarios.

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

Automatic Coverage HTML Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running ``pytest``, coverage is automatically calculated and exported as an HTML report located in the Sphinx build output at `docs/_build/html/coverage <coverage/index.html>`_.

Access the generated `Interactive HTML Code Coverage Report <coverage/index.html>`_ directly inside your built Sphinx documentation workspace.

Configuration in ``pyproject.toml``:

.. code-block:: toml

   [tool.pytest.ini_options]
   addopts = "--cov=freecad_nodegraph --cov-report=term-missing --cov-report=html:docs/_build/html/coverage --durations=0"

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
