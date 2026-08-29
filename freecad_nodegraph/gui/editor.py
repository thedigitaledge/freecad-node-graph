"""Main Node Graph Editor View widget (MDI workspace canvas view)."""

import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
)
from PySide6.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.history import GraphHistory
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView


class NodeGraphEditorWidget(QWidget):
    """Main application view widget for the FreeCAD NodeGraph editor (MDI canvas view)."""

    def __init__(self, graph: Graph = None, doc_object=None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphEditorWidget")
        self.doc_object = doc_object

        title_name = getattr(doc_object, "Label", getattr(doc_object, "Name", "NodeGraph:1"))
        self.setWindowTitle(f"{title_name}")

        self.graph = graph or Graph()
        self.history = GraphHistory()
        self._is_syncing = False

        # If bound to a document object, load graph data from object storage
        if self.doc_object:
            try:
                if hasattr(self.doc_object, "GraphData") and self.doc_object.GraphData:
                    data = json.loads(self.doc_object.GraphData)
                    GraphSerializer.from_dict(data, graph=self.graph)
            except (ReferenceError, RuntimeError, AttributeError):
                self.doc_object = None
            except Exception:
                pass

        self.scene = NodeGraphicsScene(self.graph)
        self.view = NodeGraphicsView(self.scene)

        # Record initial state in history
        initial_data = json.dumps(GraphSerializer.to_dict(self.graph))
        self.history.push_state(initial_data, description="Initial State")

        # Listen for scene graph changes to automatically save back to doc_object storage
        self.scene.changed.connect(self.save_to_document_object)
        self.scene.selectionChanged.connect(self.on_selection_changed)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.view)

    def on_selection_changed(self):
        """Update property inspector when selection changes in the scene while preserving active text input focus."""
        focus_item = self.scene.focusItem() if self.scene else None
        app_inst = QApplication.instance()
        focus_widget = app_inst.focusWidget() if app_inst else None

        selected_items = self.scene.selectedItems()
        try:
            import FreeCADGui
            if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "activeDialog"):
                dlg = FreeCADGui.Control.activeDialog()
                if hasattr(dlg, "widget") and hasattr(dlg.widget, "update_properties_inspector"):
                    dlg.widget.update_properties_inspector(selected_items)
        except Exception:
            pass

        # Restore focus to canvas view and active widget if an input control on canvas was focused
        if focus_item is not None:
            self.view.setFocus()
            focus_item.setFocus()
            if focus_widget is not None and hasattr(focus_widget, "setFocus"):
                focus_widget.setFocus()

    def save_to_document_object(self, *args):
        """Save current graph state back into the bound FreeCAD Document Object property."""
        if getattr(self, "_is_syncing", False):
            return
        if not self.doc_object:
            return

        # Defer full document transaction push while user is actively dragging items
        if self.scene and self.scene.mouseGrabberItem() is not None:
            return

        try:
            doc = getattr(self.doc_object, "Document", None)
            if doc:
                is_undo = getattr(doc, "isUndo", lambda: False)() if callable(getattr(doc, "isUndo", None)) else getattr(doc, "isUndo", False)
                is_redo = getattr(doc, "isRedo", lambda: False)() if callable(getattr(doc, "isRedo", None)) else getattr(doc, "isRedo", False)
                if is_undo or is_redo:
                    return

            data = GraphSerializer.to_dict(self.graph)
            new_json = json.dumps(data)

            if getattr(self.doc_object, "GraphData", None) == new_json:
                return

            self.history.push_state(new_json, description="Modify Node Graph")

            if hasattr(self.doc_object, "GraphData"):
                if doc and hasattr(doc, "openTransaction"):
                    try:
                        doc.openTransaction("Modify Node Graph")
                        self.doc_object.GraphData = new_json
                        doc.commitTransaction()
                    except Exception:
                        self.doc_object.GraphData = new_json
                else:
                    self.doc_object.GraphData = new_json
        except (ReferenceError, RuntimeError, AttributeError):
            self.doc_object = None
            try:
                self.scene.changed.disconnect(self.save_to_document_object)
            except Exception:
                pass

    def undo(self) -> bool:
        """Undo last modification in history stack."""
        rec = self.history.undo()
        if rec:
            self.load_state_snapshot(rec.json_data)
            return True
        return False

    def redo(self) -> bool:
        """Redo last undone modification in history stack."""
        rec = self.history.redo()
        if rec:
            self.load_state_snapshot(rec.json_data)
            return True
        return False

    def load_state_snapshot(self, json_data: str):
        """Load state snapshot into graph and scene without pushing a new history state."""
        if getattr(self, "_is_syncing", False):
            return
        self._is_syncing = True
        try:
            data = json.loads(json_data)
            try:
                self.scene.changed.disconnect(self.save_to_document_object)
            except Exception:
                pass

            self.graph.clear()
            GraphSerializer.from_dict(data, graph=self.graph)
            self.scene.sync_from_graph(preserve_selection=True)

            if self.doc_object:
                try:
                    doc = getattr(self.doc_object, "Document", None)
                    is_undo = getattr(doc, "isUndo", lambda: False)() if callable(getattr(doc, "isUndo", None)) else getattr(doc, "isUndo", False)
                    is_redo = getattr(doc, "isRedo", lambda: False)() if callable(getattr(doc, "isRedo", None)) else getattr(doc, "isRedo", False)
                    if not (is_undo or is_redo):
                        if hasattr(self.doc_object, "GraphData"):
                            self.doc_object.GraphData = json_data
                except (ReferenceError, RuntimeError, AttributeError):
                    self.doc_object = None

            try:
                self.scene.changed.connect(self.save_to_document_object)
            except Exception:
                pass
        except Exception:
            pass
        finally:
            self._is_syncing = False

    def sync_from_document_object(self):
        """Sync and re-render editor graph and scene graphics items from doc_object storage."""
        if not self.doc_object:
            return
        try:
            if hasattr(self.doc_object, "GraphData") and self.doc_object.GraphData:
                self.load_state_snapshot(self.doc_object.GraphData)
                self.history.push_state(self.doc_object.GraphData, description="Document Sync")
        except (ReferenceError, RuntimeError, AttributeError):
            self.doc_object = None

    def closeEvent(self, event):
        """Close task panel when editor view is closed."""
        try:
            import FreeCADGui
            if hasattr(FreeCADGui, "Control") and hasattr(FreeCADGui.Control, "closeDialog"):
                FreeCADGui.Control.closeDialog()
        except Exception:
            pass
        super().closeEvent(event)


# Alias for compatibility
NodeGraphEditorWindow = NodeGraphEditorWidget
