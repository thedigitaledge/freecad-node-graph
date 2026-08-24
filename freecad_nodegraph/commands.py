"""FreeCAD GUI Commands and Selection Observer for NodeGraph Workbench."""

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
from freecad_nodegraph.document_object import make_nodegraph_object

# Active document object editor registry mapping doc_object -> (subwindow, editor_widget)
_active_editors = {}
_task_panel = None
_selection_observer = None


def focus_node_library_task_panel(graph=None):
    """Focus and select the Tasks tab displaying the Node Library TaskPanel in FreeCAD."""
    global _task_panel
    if HAS_FREECAD and hasattr(FreeCADGui, "Control"):
        try:
            from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget, NodeGraphTaskPanel
            if _task_panel is None or (graph and _task_panel.widget.graph != graph):
                _task_panel = NodeGraphTaskPanel(graph=graph)
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


class NodeGraphSelectionObserver:
    """Selection observer listening for NodeGraph object selection in FreeCAD Model tree view."""

    def addSelection(self, doc_name, obj_name, sub_name, pos):
        self.check_selection(doc_name, obj_name)

    def setSelection(self, doc_name):
        pass

    def clearSelection(self, doc_name):
        pass

    def check_selection(self, doc_name, obj_name):
        if HAS_FREECAD and FreeCAD.getDocument(doc_name):
            doc = FreeCAD.getDocument(doc_name)
            obj = doc.getObject(obj_name)
            if obj and (
                getattr(obj, "Proxy", None).__class__.__name__ == "NodeGraphObject"
                or "NodeGraph" in getattr(obj, "Name", "")
            ):
                cmd = CommandOpenNodeGraphEditor()
                cmd.Activated(doc_object=obj)


class CommandCreateNodeGraphObject:
    """FreeCAD Command to create a NodeGraph document object at top level or under selected subobject."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Create",
            "MenuText": "Create NodeGraph Object",
            "ToolTip": "Creates a new NodeGraph object with its own data storage in the document (top-level or under selected group/subobject)",
        }

    def Activated(self):
        if HAS_FREECAD and FreeCAD.ActiveDocument:
            doc = FreeCAD.ActiveDocument
            sel = FreeCADGui.Selection.getSelection()
            parent_obj = sel[0] if sel else None

            obj = make_nodegraph_object(doc=doc, name="NodeGraph", parent_obj=parent_obj)
            doc.recompute()

            # Instantly open and display the new NodeGraph object's editor window
            cmd = CommandOpenNodeGraphEditor()
            cmd.Activated(doc_object=obj)

            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintMessage(f"Created NodeGraph object: {obj.Name}\n")

    def IsActive(self):
        return True if (HAS_FREECAD and FreeCAD.ActiveDocument) else False


class CommandOpenNodeGraphEditor:
    """FreeCAD Command to open Node Graph Editor bound to a specific document object storage."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Editor",
            "MenuText": "Open Node Graph",
            "ToolTip": "Opens the Node Graph editor view for the selected or active document object data storage",
        }

    def Activated(self, doc_object=None):
        global _active_editors
        try:
            from freecad_nodegraph.gui.editor import (
                NodeGraphEditorWidget,
                set_editor_activated_callback,
            )

            # Determine target document object
            if doc_object is None and HAS_FREECAD and hasattr(FreeCADGui, "Selection"):
                sel = FreeCADGui.Selection.getSelection()
                if sel:
                    for item in sel:
                        if getattr(item, "Proxy", None).__class__.__name__ == "NodeGraphObject" or "NodeGraph" in item.Name:
                            doc_object = item
                            break

            if doc_object is None and HAS_FREECAD and FreeCAD.ActiveDocument:
                # Find first NodeGraph object in active document
                for obj in FreeCAD.ActiveDocument.Objects:
                    if getattr(obj, "Proxy", None).__class__.__name__ == "NodeGraphObject" or "NodeGraph" in obj.Name:
                        doc_object = obj
                        break

            # If no document object exists yet, create one
            if doc_object is None and HAS_FREECAD and FreeCAD.ActiveDocument:
                doc_object = make_nodegraph_object(doc=FreeCAD.ActiveDocument, name="NodeGraph")

            # Set global callback so selecting/activating the NodeGraph editor shows Node Library in Tasks view
            set_editor_activated_callback(
                lambda editor: focus_node_library_task_panel(graph=editor.graph)
            )

            if HAS_FREECAD and hasattr(FreeCADGui, "getMainWindow"):
                main_win = FreeCADGui.getMainWindow()
                mdi_area = main_win.findChild(QMdiArea)

                subwin_info = _active_editors.get(doc_object)
                if subwin_info is None or not subwin_info[0].isVisible():
                    editor_widget = NodeGraphEditorWidget(doc_object=doc_object)
                    if mdi_area:
                        subwin = mdi_area.addSubWindow(editor_widget)
                        obj_title = getattr(doc_object, "Label", getattr(doc_object, "Name", "NodeGraph"))
                        subwin.setWindowTitle(f"NodeGraph Editor - {obj_title}")
                        subwin.showMaximized()
                        _active_editors[doc_object] = (subwin, editor_widget)
                    else:
                        editor_widget.show()
                        _active_editors[doc_object] = (editor_widget, editor_widget)
                else:
                    subwin, editor_widget = subwin_info
                    subwin.show()
                    subwin.raise_()

                focus_node_library_task_panel(graph=editor_widget.graph)

            else:
                # Standalone fallback mode
                subwin_info = _active_editors.get(doc_object)
                if subwin_info is None:
                    editor_widget = NodeGraphEditorWidget(doc_object=doc_object)
                    _active_editors[doc_object] = (editor_widget, editor_widget)
                    editor_widget.show()
                else:
                    editor_widget = subwin_info[1]
                    editor_widget.show()

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
        try:
            if HAS_FREECAD and FreeCAD.ActiveDocument:
                FreeCAD.ActiveDocument.recompute()
                if hasattr(FreeCAD, "Console"):
                    FreeCAD.Console.PrintMessage("Evaluated document NodeGraph objects.\n")
        except Exception as e:
            if HAS_FREECAD and hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"NodeGraph Error: {e}\n")
            else:
                print(f"NodeGraph Error: {e}")

    def IsActive(self):
        return True


def register_commands():
    global _selection_observer
    if HAS_FREECAD:
        FreeCADGui.addCommand("NodeGraph_CreateObject", CommandCreateNodeGraphObject())
        FreeCADGui.addCommand("NodeGraph_OpenEditor", CommandOpenNodeGraphEditor())
        FreeCADGui.addCommand("NodeGraph_RunGraph", CommandRunNodeGraph())

        if _selection_observer is None and hasattr(FreeCADGui, "Selection"):
            _selection_observer = NodeGraphSelectionObserver()
            FreeCADGui.Selection.addObserver(_selection_observer)
