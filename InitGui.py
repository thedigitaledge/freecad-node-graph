# FreeCAD Gui init script for NodeGraph Workbench
# Executed when FreeCAD GUI initializes

import os
import sys

# Compute BASE_DIR safely without requiring __file__ in global scope
try:
    import FreeCAD
    import FreeCADGui
    has_freecad = True
except ImportError:
    has_freecad = False

if "__file__" in globals() and __file__:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
elif has_freecad and hasattr(FreeCAD, "getUserAppDataDir"):
    BASE_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "NodeGraph")
else:
    BASE_DIR = os.getcwd()

# Ensure workbench directory is in sys.path
if BASE_DIR and BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

ICONS_DIR = os.path.join(BASE_DIR, "freecad_nodegraph", "resources", "icons")

if has_freecad and hasattr(FreeCADGui, "addIconPath"):
    FreeCADGui.addIconPath(ICONS_DIR)


class NodeGraphWorkbench(FreeCADGui.Workbench if has_freecad else object):
    """FreeCAD NodeGraph Workbench definition."""

    MenuText = "NodeGraph"
    ToolTip = "Programming FreeCAD features using a node-graph"
    Icon = os.path.join(ICONS_DIR, "NodeGraph_Workbench.svg")
    _icons_dir = ICONS_DIR

    def __init__(self):
        super().__init__()

    def Initialize(self):
        """Initialize workbench commands, toolbars and menus."""
        try:
            import FreeCADGui
            if hasattr(FreeCADGui, "addIconPath"):
                FreeCADGui.addIconPath(self._icons_dir)
        except Exception:
            pass

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


if has_freecad:
    FreeCADGui.addIconPath(ICONS_DIR)
    FreeCADGui.addWorkbench(NodeGraphWorkbench())
