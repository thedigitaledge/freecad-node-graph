Installation & Documentation Setup
====================================

Requirements
------------

- FreeCAD 0.20 or newer.
- Python 3.8+
- PySide6 (included with modern FreeCAD installations or installed via pip).

Building Documentation (Primary Method)
----------------------------------------

Local offline generation using Sphinx is the **primary method** for creating and building workbench documentation:

1. Install documentation dependencies:

   .. code-block:: bash

      pip install .[docs]

2. Generate HTML documentation locally offline:

   .. code-block:: bash

      sphinx-build -b html docs docs/_build/html

3. Open ``docs/_build/html/index.html`` in a web browser to view offline documentation.

How to Load in FreeCAD
----------------------

To install and load the NodeGraph Workbench into FreeCAD:

1. Locate your FreeCAD user directory or ``Mod`` folder:

   - **Linux**: ``~/.local/share/FreeCAD/Mod/`` or ``~/.FreeCAD/Mod/``
   - **Windows**: ``%APPDATA%\FreeCAD\Mod\``
   - **macOS**: ``~/Library/Application Support/FreeCAD/Mod/``

2. Copy or clone the repository into the ``Mod`` directory:

   .. code-block:: bash

      cd ~/.local/share/FreeCAD/Mod/
      git clone https://github.com/freecad/freecad-nodegraph.git NodeGraph

3. Launch FreeCAD.

4. Open the Workbench selector menu from the top toolbar and select **NodeGraph**.

5. The NodeGraph toolbar with **Open Node Graph Editor** and **Run Node Graph** actions will appear.
