# FreeCAD Gui init script for NodeGraph Workbench
# Executed when FreeCAD GUI initializes

import os
from freecad_nodegraph.resources import ICONS_DIR

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False


class NodeGraphWorkbench(FreeCADGui.Workbench if HAS_FREECAD else object):
    """FreeCAD NodeGraph Workbench definition."""

    MenuText = "NodeGraph"
    ToolTip = "Programming FreeCAD features using a node-graph"
    Icon = os.path.join(ICONS_DIR, "NodeGraph_Workbench.svg")

    def __init__(self):
        super().__init__()

    def Initialize(self):
        """Initialize workbench commands, toolbars and menus."""
        import freecad_nodegraph.commands as commands
        commands.register_commands()

        if HAS_FREECAD and hasattr(FreeCADGui, "addIconPath"):
            FreeCADGui.addIconPath(ICONS_DIR)

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
