"""FreeCAD GUI Commands and Selection Observer for NodeGraph Workbench."""

try:
    import FreeCAD
    import FreeCADGui
except ImportError:
    FreeCAD = None
    FreeCADGui = None

from PySide6.QtWidgets import QMdiSubWindow, QMdiArea, QDockWidget, QTabWidget
from PySide6.QtCore import Qt

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
_selection_observer = None


def get_active_editor():
    """Retrieve currently active or focused NodeGraphEditorWidget."""
    if hasattr(FreeCADGui, "getMainWindow") and FreeCADGui.getMainWindow():
        main_win = FreeCADGui.getMainWindow()
        if main_win:
            mdi_area = main_win.findChild(QMdiArea)
            if mdi_area and mdi_area.activeSubWindow():
                subwin = mdi_area.activeSubWindow()
                widget = subwin.widget() if hasattr(subwin, "widget") else None
                if widget is not None and widget.__class__.__name__ == "NodeGraphEditorWidget":
                    return widget

    if _active_editors:
        for doc_obj, (subwin, editor) in reversed(list(_active_editors.items())):
            if hasattr(subwin, "isVisible") and subwin.isVisible():
                return editor

    return None


def show_task_panel_safely(graph):
    """Safely display NodeGraphTaskPanel in FreeCAD Tasks view, closing active dialog if present."""
    if hasattr(FreeCADGui, "Control"):
        try:
            if hasattr(FreeCADGui.Control, "activeDialog") and FreeCADGui.Control.activeDialog() is not None:
                FreeCADGui.Control.closeDialog()
        except Exception:
            pass

        try:
            from freecad_nodegraph.gui.panel import NodeGraphTaskPanel
            task_panel = NodeGraphTaskPanel(graph=graph)
            FreeCADGui.Control.showDialog(task_panel)
        except Exception:
            try:
                if hasattr(FreeCADGui.Control, "closeDialog"):
                    FreeCADGui.Control.closeDialog()
                from freecad_nodegraph.gui.panel import NodeGraphTaskPanel
                task_panel = NodeGraphTaskPanel(graph=graph)
                FreeCADGui.Control.showDialog(task_panel)
            except Exception as ex:
                if hasattr(FreeCAD, "Console"):
                    FreeCAD.Console.PrintError(f"Error displaying TaskPanel: {ex}\n")


def on_subwindow_activated(subwin):
    """Handle MDI subwindow focus changes to activate/deactivate the Node Graph TaskPanel."""
    if subwin is None:
        if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "closeDialog"):
            try:
                FreeCADGui.Control.closeDialog()
            except Exception:
                pass
        return

    widget = subwin.widget() if hasattr(subwin, "widget") else None
    if widget is not None and widget.__class__.__name__ == "NodeGraphEditorWidget":
        show_task_panel_safely(widget.graph)
    else:
        if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "closeDialog"):
            try:
                FreeCADGui.Control.closeDialog()
            except Exception:
                pass


class NodeGraphSelectionObserver:
    """Selection observer listening for NodeGraph object selection in FreeCAD Model tree view."""

    def addSelection(self, doc_name, obj_name, sub_name, pos):
        self.check_selection(doc_name, obj_name)

    def setSelection(self, doc_name):
        pass

    def clearSelection(self, doc_name):
        self.close_task_panel()

    def close_task_panel(self):
        if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "closeDialog"):
            try:
                FreeCADGui.Control.closeDialog()
            except Exception:
                pass

    def check_selection(self, doc_name, obj_name):
        if FreeCAD and hasattr(FreeCAD, "getDocument") and FreeCAD.getDocument(doc_name):
            doc = FreeCAD.getDocument(doc_name)
            obj = doc.getObject(obj_name)
            if obj and (
                getattr(obj, "Proxy", None).__class__.__name__ == "NodeGraphObject"
                or getattr(obj, "Name", "").startswith("NodeGraph")
                or getattr(obj, "Label", "").startswith("NodeGraph")
            ):
                cmd = CommandOpenNodeGraphEditor()
                cmd.Activated(doc_object=obj)
            else:
                self.close_task_panel()


class CommandCreateNodeGraphObject:
    """FreeCAD Command to create a NodeGraph document object as a top level or nested child object."""

    def GetResources(self):
        return {
            "Pixmap": "NodeGraph_Create",
            "MenuText": "Create NodeGraph Object",
            "ToolTip": "Creates a new NodeGraph object (nested as a child if a parent object is selected in Model view)",
        }

    def Activated(self):
        if FreeCAD.ActiveDocument:
            doc = FreeCAD.ActiveDocument
            sel = FreeCADGui.Selection.getSelection()
            parent_obj = sel[0] if sel else None

            obj = make_nodegraph_object(doc=doc, parent_obj=parent_obj)
            doc.recompute()

            # Instantly open and display the new NodeGraph object's editor window and tasks overlay panel
            cmd = CommandOpenNodeGraphEditor()
            cmd.Activated(doc_object=obj)
            if hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintMessage(f"Created NodeGraph object: {obj.Label}\n")

    def IsActive(self):
        return True if FreeCAD.ActiveDocument else False


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
            from freecad_nodegraph.gui.editor import NodeGraphEditorWidget

            # Determine target document object
            if doc_object is None and hasattr(FreeCADGui, "Selection"):
                sel = FreeCADGui.Selection.getSelection()
                if sel:
                    for item in sel:
                        if (
                            getattr(item, "Proxy", None).__class__.__name__
                            == "NodeGraphObject"
                            or getattr(item, "Name", "").startswith("NodeGraph")
                            or getattr(item, "Label", "").startswith("NodeGraph")
                        ):
                            doc_object = item
                            break

            if doc_object is None and FreeCAD.ActiveDocument:
                # Find first NodeGraph object in active document
                for obj in FreeCAD.ActiveDocument.Objects:
                    if (
                        getattr(obj, "Proxy", None).__class__.__name__
                        == "NodeGraphObject"
                        or getattr(obj, "Name", "").startswith("NodeGraph")
                        or getattr(obj, "Label", "").startswith("NodeGraph")
                    ):
                        doc_object = obj
                        break

            # If no document object exists yet, create one
            if doc_object is None and FreeCAD.ActiveDocument:
                sel = FreeCADGui.Selection.getSelection()
                parent_obj = sel[0] if sel else None
                doc_object = make_nodegraph_object(
                    doc=FreeCAD.ActiveDocument, parent_obj=parent_obj
                )

            obj_title = getattr(
                doc_object, "Label", getattr(doc_object, "Name", "NodeGraph:1")
            )

            from freecad_nodegraph.gui.panel import NodeGraphTaskPanel

            if hasattr(FreeCADGui, "getMainWindow"):
                main_win = FreeCADGui.getMainWindow()
                mdi_area = main_win.findChild(QMdiArea) if main_win else None
                if mdi_area and not getattr(mdi_area, "_nodegraph_connected", False):
                    try:
                        mdi_area.subWindowActivated.connect(on_subwindow_activated)
                        setattr(mdi_area, "_nodegraph_connected", True)
                    except Exception:
                        pass

                subwin_info = _active_editors.get(doc_object)
                if subwin_info is None or not subwin_info[0].isVisible():
                    editor_widget = NodeGraphEditorWidget(doc_object=doc_object)
                    if mdi_area:
                        subwin = mdi_area.addSubWindow(editor_widget)
                        subwin.setWindowTitle(f"{obj_title}")
                        subwin.show()
                        subwin.showMaximized()
                        editor_widget.showMaximized()
                        mdi_area.setActiveSubWindow(subwin)
                        _active_editors[doc_object] = (subwin, editor_widget)
                    else:
                        editor_widget.setWindowTitle(f"{obj_title}")
                        editor_widget.showMaximized()
                        _active_editors[doc_object] = (editor_widget, editor_widget)
                else:
                    subwin, editor_widget = subwin_info
                    subwin.show()
                    subwin.showMaximized()
                    subwin.raise_()
                    if mdi_area:
                        mdi_area.setActiveSubWindow(subwin)

            else:
                # Standalone fallback mode
                subwin_info = _active_editors.get(doc_object)
                if subwin_info is None:
                    editor_widget = NodeGraphEditorWidget(doc_object=doc_object)
                    editor_widget.setWindowTitle(f"{obj_title}")
                    _active_editors[doc_object] = (editor_widget, editor_widget)
                    editor_widget.showMaximized()
                else:
                    editor_widget = subwin_info[1]
                    editor_widget.showMaximized()

            # Integrate Node Library into FreeCAD's task view combo box
            show_task_panel_safely(editor_widget.graph)

        except Exception as e:
            if hasattr(FreeCAD, "Console"):
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
            if FreeCAD.ActiveDocument:
                FreeCAD.ActiveDocument.recompute()
                if hasattr(FreeCAD, "Console"):
                    FreeCAD.Console.PrintMessage(
                        "Evaluated document NodeGraph objects.\n"
                    )
        except Exception as e:
            if hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintError(f"NodeGraph Error: {e}\n")
            else:
                print(f"NodeGraph Error: {e}")

    def IsActive(self):
        return True


def register_commands():
    global _selection_observer
    FreeCADGui.addCommand("NodeGraph_CreateObject", CommandCreateNodeGraphObject())
    FreeCADGui.addCommand("NodeGraph_OpenEditor", CommandOpenNodeGraphEditor())
    FreeCADGui.addCommand("NodeGraph_RunGraph", CommandRunNodeGraph())

    if _selection_observer is None and hasattr(FreeCADGui, "Selection"):
        _selection_observer = NodeGraphSelectionObserver()
        FreeCADGui.Selection.addObserver(_selection_observer)
