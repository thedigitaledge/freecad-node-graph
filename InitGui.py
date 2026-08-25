# FreeCAD Gui init script for NodeGraph Workbench
# Executed when FreeCAD GUI initializes

import FreeCAD
import FreeCADGui


class NodeGraphWorkbench(FreeCADGui.Workbench):
    """FreeCAD NodeGraph Workbench definition."""

    MenuText = "NodeGraph"
    ToolTip = "Programming FreeCAD features using a node-graph"

    def __init__(self):
        super().__init__()

    def Initialize(self):
        """Initialize workbench commands, toolbars and menus."""
        import freecad_nodegraph.commands as commands

        commands.register_commands()

        cmd_list = [
            "NodeGraph_CreateObject",
            "NodeGraph_OpenEditor",
            "NodeGraph_RunGraph",
        ]
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


if __name__ == "__main__":
    FreeCADGui.addWorkbench(NodeGraphWorkbench())
