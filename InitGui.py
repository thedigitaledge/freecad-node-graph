# FreeCAD Gui init script for NodeGraph Workbench
# Executed when FreeCAD GUI initializes

import os
import sys

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False

# Safely compute BASE_DIR without requiring __file__ to be defined in global scope
if "__file__" in globals() and __file__:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
elif HAS_FREECAD and hasattr(FreeCAD, "getUserAppDataDir"):
    BASE_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "NodeGraph")
else:
    BASE_DIR = os.getcwd()

# Ensure workbench directory is in sys.path
if BASE_DIR and BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

ICONS_DIR = os.path.join(BASE_DIR, "freecad_nodegraph", "resources", "icons")

if HAS_FREECAD and hasattr(FreeCADGui, "addIconPath"):
    FreeCADGui.addIconPath(ICONS_DIR)


class NodeGraphWorkbench(FreeCADGui.Workbench if HAS_FREECAD else object):
    """FreeCAD NodeGraph Workbench definition."""

    MenuText = "NodeGraph"
    ToolTip = "Programming FreeCAD features using a node-graph"
    Icon = "NodeGraph_Workbench"  # References NodeGraph_Workbench.svg registered in addIconPath

    def __init__(self):
        super().__init__()

    def Initialize(self):
        """Initialize workbench commands, toolbars and menus."""
        if HAS_FREECAD and hasattr(FreeCADGui, "addIconPath"):
            FreeCADGui.addIconPath(ICONS_DIR)

        import freecad_nodegraph.commands as commands
        commands.register_commands()

        cmd_list = ["NodeGraph_CreateObject", "NodeGraph_OpenEditor", "NodeGraph_RunGraph"]
        self.appendToolbar("NodeGraph", cmd_list)
        self.appendMenu("NodeGraph", cmd_list)

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Activated(self):
        """Executed when workbench is activated."""
        pass

    def Deactivated(self):
        """Executed when workbench is deactivated."""
        pass


if HAS_FREECAD:
    FreeCADGui.addIconPath(ICONS_DIR)
    FreeCADGui.addWorkbench(NodeGraphWorkbench())
