"""FreeCAD GUI Commands for NodeGraph Workbench."""

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False

try:
    from PySide6.QtWidgets import QMdiSubWindow, QMdiArea, QDockWidget, QTabWidget
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import QMdiSubWindow, QMdiArea, QDockWidget, QTabWidget
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import QMdiSubWindow, QMdiArea, QDockWidget, QTabWidget
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator

global_graph = Graph()
_mdi_subwindow = None
_task_panel = None


def focus_node_library_task_panel():
    """Focus and select the Tasks tab displaying the Node Library TaskPanel in FreeCAD."""
    global _task_panel, global_graph
    if HAS_FREECAD and hasattr(FreeCADGui, "Control"):
        try:
            from freecad_nodegraph.gui.panel import NodeGraphTaskPanel
            if _task_panel is None:
                _task_panel = NodeGraphTaskPanel(graph=global_graph)
            FreeCADGui.Control.showDialog(_task_panel)
            return True
        except Exception:
            pass

    if HAS_FREECAD and hasattr(FreeCADGui, "getMainWindow"):
        main_win = FreeCADGui.getMainWindow()
        combo_view = main_win.findChild(QDockWidget, "Combo View") or main_win.findChild(QDockWidget, "ComboView")
        if combo_view:
            tab_widget = combo_view.findChild(QTabWidget)
            if tab_widget:
                for idx in range(tab_widget.count()):
                    if tab_widget.tabText(idx) in ("Tasks", "Task"):
                        tab_widget.setCurrentIndex(idx)
                        return True
    return False


class CommandOpenNodeGraphEditor:
    """FreeCAD Command to open Node Graph Editor inside FreeCAD MDI area and Node Library in Tasks view."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Editor",
            "MenuText": "Open Node Graph",
            "ToolTip": "Opens the Node Graph editor view in FreeCAD main window area and Node Library in Tasks view",
        }

    def Activated(self):
        global _mdi_subwindow, _task_panel, global_graph
        try:
            from freecad_nodegraph.gui.editor import (
                NodeGraphEditorWidget,
                set_editor_activated_callback,
            )

            # Set global callback so selecting/activating the NodeGraph editor shows Node Library in Tasks view
            set_editor_activated_callback(lambda editor: focus_node_library_task_panel())

            if HAS_FREECAD and hasattr(FreeCADGui, "getMainWindow"):
                main_win = FreeCADGui.getMainWindow()

                # 1. Open MDI View tab (matching Spreadsheet window style)
                mdi_area = main_win.findChild(QMdiArea)
                if _mdi_subwindow is None or not _mdi_subwindow.isVisible():
                    editor_widget = NodeGraphEditorWidget(graph=global_graph)
                    if mdi_area:
                        _mdi_subwindow = mdi_area.addSubWindow(editor_widget)
                        _mdi_subwindow.setWindowTitle("NodeGraph Editor")
                        _mdi_subwindow.showMaximized()
                    else:
                        _mdi_subwindow = editor_widget
                        _mdi_subwindow.show()
                else:
                    _mdi_subwindow.show()
                    _mdi_subwindow.raise_()

                # 2. Display Node Library in Tasks view panel
                focus_node_library_task_panel()

            else:
                # Standalone fallback mode
                if _mdi_subwindow is None:
                    _mdi_subwindow = NodeGraphEditorWidget(graph=global_graph)
                _mdi_subwindow.show()

        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"Error opening Node Graph: {e}\n")
            else:
                print(f"Error opening Node Graph: {e}")

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
