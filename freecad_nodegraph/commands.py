"""FreeCAD GUI Commands for NodeGraph Workbench."""

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False

try:
    from PySide6.QtWidgets import QDockWidget
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import QDockWidget
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import QDockWidget
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator

global_graph = Graph()
_dock_widget = None


class CommandOpenNodeGraphEditor:
    """FreeCAD Command to open Node Graph Editor embedded view dock."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Editor",
            "MenuText": "Open Node Graph View",
            "ToolTip": "Opens the Node Graph visual editor view embedded in FreeCAD",
        }

    def Activated(self):
        global _dock_widget, global_graph
        try:
            from freecad_nodegraph.gui.editor import NodeGraphEditorWidget

            if HAS_FREECAD and hasattr(FreeCADGui, "getMainWindow"):
                main_win = FreeCADGui.getMainWindow()
                if _dock_widget is None or _dock_widget.parent() is None:
                    _dock_widget = QDockWidget("Node Graph Editor", main_win)
                    _dock_widget.setObjectName("NodeGraphDockWidget")
                    editor_widget = NodeGraphEditorWidget(graph=global_graph, parent=_dock_widget)
                    _dock_widget.setWidget(editor_widget)
                    main_win.addDockWidget(Qt.BottomDockWidgetArea, _dock_widget)

                _dock_widget.show()
                _dock_widget.raise_()
            else:
                # Standalone fallback mode
                if _dock_widget is None:
                    _dock_widget = NodeGraphEditorWidget(graph=global_graph)
                _dock_widget.show()
        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"Error opening Node Graph View: {e}\n")
            else:
                print(f"Error opening Node Graph View: {e}")

    def IsActive(self):
        return True


class CommandRunNodeGraph:
    """FreeCAD Command to evaluate active Node Graph."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Run",
            "MenuText": "Run Node Graph",
            "ToolTip": "Executes the current node graph and updates the active document",
        }

    def Activated(self):
        global global_graph
        try:
            evaluator = GraphEvaluator(global_graph)
            evaluated = evaluator.evaluate(force=True)
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintMessage(f"NodeGraph: Evaluated {len(evaluated)} nodes.\n")
        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"NodeGraph Error: {e}\n")
            else:
                print(f"NodeGraph Error: {e}")

    def IsActive(self):
        return True


def register_commands():
    if HAS_FREECAD:
        FreeCADGui.addCommand("NodeGraph_OpenEditor", CommandOpenNodeGraphEditor())
        FreeCADGui.addCommand("NodeGraph_RunGraph", CommandRunNodeGraph())
