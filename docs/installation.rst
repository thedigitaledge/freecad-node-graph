Installation & FreeCAD Setup
============================

Requirements
------------

- FreeCAD 0.20 or newer.
- Python 3.8+
- PySide6, PySide2, or PyQt5 (included with standard FreeCAD installations).

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
