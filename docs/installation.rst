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

3. Serve and view the built HTML documentation locally:

   .. code-block:: bash

      python3 -m http.server -d docs/_build/html

   Then navigate to ``http://localhost:8000`` in your browser to view the offline documentation.

How to Load in FreeCAD
----------------------

To install and load the NodeGraph Workbench into FreeCAD:

1. Locate your FreeCAD user directory or ``Mod`` folder:

   - **Linux**:

     - Standard installation: ``~/.local/share/FreeCAD/Mod/`` or ``~/.FreeCAD/Mod/``
     - Flatpak installation: ``~/.var/app/org.freecad.FreeCAD/data/FreeCAD/Mod/``
     - Running via Flatpak:

       .. code-block:: bash

          flatpak run org.freecad.FreeCAD

     - Specifying a custom module directory with the ``-M`` option:

       .. code-block:: bash

          # Native FreeCAD executable:
          freecad -M /path/to/custom/Mod

          # Flatpak FreeCAD installation:
          flatpak run org.freecad.FreeCAD -M /path/to/custom/Mod

   - **Windows**: ``%APPDATA%\FreeCAD\Mod\``
   - **macOS**: ``~/Library/Application Support/FreeCAD/Mod/``

2. Copy or clone the repository into the ``Mod`` directory:

   .. code-block:: bash

      cd ~/.local/share/FreeCAD/Mod/
      git clone https://github.com/freecad/freecad-nodegraph.git NodeGraph

3. Launch FreeCAD.

4. Open the Workbench selector menu from the top toolbar and select **NodeGraph**.

5. The NodeGraph toolbar with **Open Node Graph Editor** and **Run Node Graph** actions will appear.
