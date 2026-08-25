"""FreeCAD GUI Commands for NodeGraph Workbench."""

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False

try:
    from PySide6.QtWidgets import QMdiArea
except ImportError:
    try:
        from PySide2.QtWidgets import QMdiArea
    except ImportError:
        try:
            from PyQt5.QtWidgets import QMdiArea
        except ImportError:
            QMdiArea = None

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator

global_graph = Graph()
_editor_window = None
_task_panel = None
_property_inspector = None


class CommandOpenNodeGraphEditor:
    """FreeCAD Command to open Node Graph Editor MDI view tab, Task Panel, and Model tab Property Inspector."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Editor",
            "MenuText": "Open Node Graph Editor",
            "ToolTip": "Opens the Node Graph visual editor MDI view tab, Task Panel, and Model tab Property Inspector",
        }

    def Activated(self):
        global _editor_window, _task_panel, _property_inspector, global_graph
        try:
            from freecad_nodegraph.gui.editor import (
                NodeGraphEditorWindow,
                NodeGraphTaskPanel,
                NodePropertyInspector,
            )

            if HAS_FREECAD:
                mw = FreeCADGui.getMainWindow() if hasattr(FreeCADGui, "getMainWindow") else None
                mdi_area = mw.findChild(QMdiArea) if (mw and QMdiArea) else None

                if _editor_window is None or not _editor_window.isVisible():
                    _editor_window = NodeGraphEditorWindow(graph=global_graph, title="NodeGraph")
                    _task_panel = NodeGraphTaskPanel(editor_window=_editor_window)
                    _property_inspector = NodePropertyInspector(editor_window=_editor_window)

                    _editor_window.set_task_panel(_task_panel)
                    _editor_window.set_property_inspector(_property_inspector)
                    _property_inspector.embed_in_model_tab_base()

                    if mdi_area:
                        sub_window = mdi_area.addSubWindow(_editor_window)
                        sub_window.setWindowTitle("NodeGraph")
                        sub_window.show()
                        mdi_area.setActiveSubWindow(sub_window)
                    else:
                        _editor_window.show()

                    if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "showDialog"):
                        FreeCADGui.Control.showDialog(_task_panel)
                else:
                    if hasattr(_editor_window, "parentWidget") and _editor_window.parentWidget():
                        _editor_window.parentWidget().raise_()
                    _editor_window.raise_()
                    _editor_window.activateWindow()
                    if _task_panel and hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "showDialog"):
                        FreeCADGui.Control.showDialog(_task_panel)
            else:
                if _editor_window is None or not _editor_window.isVisible():
                    _editor_window = NodeGraphEditorWindow(graph=global_graph, title="NodeGraph")
                    _task_panel = NodeGraphTaskPanel(editor_window=_editor_window)
                    _property_inspector = NodePropertyInspector(editor_window=_editor_window)

                    _editor_window.set_task_panel(_task_panel)
                    _editor_window.set_property_inspector(_property_inspector)
                    _editor_window.show()
                else:
                    _editor_window.raise_()
                    _editor_window.activateWindow()

        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"Error opening Node Graph Editor: {e}\n")
            else:
                print(f"Error opening Node Graph Editor: {e}")

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
