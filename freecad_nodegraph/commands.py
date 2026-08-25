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
from freecad_nodegraph.document_object import create_nodegraph_object

global_graph = Graph()
_editor_windows = {}
_task_panel = None
_property_inspector = None


def open_editor_for_nodegraph_object(node_obj):
    """Open or focus the MDI editor workspace view tab and Task Panel for a NodeGraph document object."""
    global _editor_windows, _task_panel, _property_inspector
    try:
        from freecad_nodegraph.gui.editor import (
            NodeGraphEditorWindow,
            NodeGraphTaskPanel,
            NodePropertyInspector,
        )

        obj_id = getattr(node_obj, "Name", id(node_obj))
        label_title = getattr(node_obj, "Label", "NodeGraph")

        if HAS_FREECAD:
            mw = FreeCADGui.getMainWindow() if hasattr(FreeCADGui, "getMainWindow") else None
            mdi_area = mw.findChild(QMdiArea) if (mw and QMdiArea) else None

            editor_win = _editor_windows.get(obj_id)
            if editor_win is None or not editor_win.isVisible():
                editor_win = NodeGraphEditorWindow(title=label_title, doc_object=node_obj)
                _editor_windows[obj_id] = editor_win

                if _task_panel is None:
                    _task_panel = NodeGraphTaskPanel(editor_window=editor_win)
                else:
                    _task_panel.set_editor_window(editor_win)

                if _property_inspector is None:
                    _property_inspector = NodePropertyInspector(editor_window=editor_win)
                    _property_inspector.embed_in_model_tab_base()
                else:
                    _property_inspector.set_editor_window(editor_win)

                editor_win.set_task_panel(_task_panel)
                editor_win.set_property_inspector(_property_inspector)

                if mdi_area:
                    sub_window = mdi_area.addSubWindow(editor_win)
                    sub_window.setWindowTitle(label_title)
                    sub_window.show()
                    mdi_area.setActiveSubWindow(sub_window)
                else:
                    editor_win.show()

                if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "showDialog"):
                    FreeCADGui.Control.showDialog(_task_panel)
            else:
                if hasattr(editor_win, "parentWidget") and editor_win.parentWidget():
                    editor_win.parentWidget().raise_()
                editor_win.raise_()
                editor_win.activateWindow()
                if _task_panel:
                    _task_panel.set_editor_window(editor_win)
                    if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "showDialog"):
                        FreeCADGui.Control.showDialog(_task_panel)
                if _property_inspector:
                    _property_inspector.set_editor_window(editor_win)
            return editor_win
        else:
            editor_win = _editor_windows.get(obj_id)
            if editor_win is None or not editor_win.isVisible():
                editor_win = NodeGraphEditorWindow(title=label_title, doc_object=node_obj)
                _editor_windows[obj_id] = editor_win

                if _task_panel is None:
                    _task_panel = NodeGraphTaskPanel(editor_window=editor_win)
                else:
                    _task_panel.set_editor_window(editor_win)

                if _property_inspector is None:
                    _property_inspector = NodePropertyInspector(editor_window=editor_win)
                else:
                    _property_inspector.set_editor_window(editor_win)

                editor_win.set_task_panel(_task_panel)
                editor_win.set_property_inspector(_property_inspector)
                editor_win.show()
            else:
                editor_win.raise_()
                editor_win.activateWindow()
            return editor_win
    except Exception as e:
        if HAS_FREECAD and hasattr(FreeCAD, "Console"):
            FreeCAD.Console.PrintError(f"Error opening NodeGraph editor: {e}\n")
        else:
            print(f"Error opening NodeGraph editor: {e}")
        return None


class CommandCreateNodeGraph:
    """FreeCAD Command to create a new NodeGraph document object in active document tree."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Editor",
            "MenuText": "Create New Node Graph",
            "ToolTip": "Creates a new NodeGraph document object in the active document model tree",
        }

    def Activated(self):
        try:
            parent_obj = None
            if HAS_FREECAD and hasattr(FreeCADGui, "Selection"):
                selected = FreeCADGui.Selection.getSelection()
                if selected:
                    parent_obj = selected[0]

            node_obj = create_nodegraph_object(parent_obj=parent_obj)
            open_editor_for_nodegraph_object(node_obj)
        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"Error creating NodeGraph document object: {e}\n")
            else:
                print(f"Error creating NodeGraph document object: {e}")

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


# Alias CommandOpenNodeGraphEditor to CommandCreateNodeGraph for backwards compatibility
CommandOpenNodeGraphEditor = CommandCreateNodeGraph


def register_commands():
    if HAS_FREECAD:
        FreeCADGui.addCommand("NodeGraph_CreateGraph", CommandCreateNodeGraph())
        FreeCADGui.addCommand("NodeGraph_OpenEditor", CommandOpenNodeGraphEditor())
        FreeCADGui.addCommand("NodeGraph_RunGraph", CommandRunNodeGraph())
