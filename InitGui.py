# FreeCAD Gui init script for NodeGraph Workbench
# Executed when FreeCAD GUI initializes

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

    def __init__(self):
        super().__init__()

    def Initialize(self):
        """Initialize workbench commands, toolbars and menus."""
        import freecad_nodegraph.commands as commands
        commands.register_commands()

        self.appendToolbar("NodeGraph", ["NodeGraph_CreateGraph", "NodeGraph_RunGraph"])
        self.appendMenu("NodeGraph", ["NodeGraph_CreateGraph", "NodeGraph_RunGraph"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Activated(self):
        """Executed when workbench is activated."""
        pass

    def Deactivated(self):
        """Executed when workbench is deactivated."""
        pass


if HAS_FREECAD:
    FreeCADGui.addWorkbench(NodeGraphWorkbench())
