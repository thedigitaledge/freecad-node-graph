"""Main Node Graph Editor View widget (MDI workspace canvas view)."""

import json
try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
    )
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
        )
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
        )
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
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

        # If bound to a document object, load graph data from object storage
        if self.doc_object and hasattr(self.doc_object, "GraphData") and self.doc_object.GraphData:
            try:
                data = json.loads(self.doc_object.GraphData)
                GraphSerializer.from_dict(data, graph=self.graph)
            except Exception:
                pass

        self.scene = NodeGraphicsScene(self.graph)
        self.view = NodeGraphicsView(self.scene)

        # Listen for scene graph changes to automatically save back to doc_object storage
        self.scene.changed.connect(self.save_to_document_object)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.view)

    def save_to_document_object(self, *args):
        """Save current graph state back into the bound FreeCAD Document Object property."""
        if self.doc_object and hasattr(self.doc_object, "GraphData"):
            data = GraphSerializer.to_dict(self.graph)
            new_json = json.dumps(data)

            if getattr(self.doc_object, "GraphData", None) == new_json:
                return

            doc = getattr(self.doc_object, "Document", None)
            if doc and hasattr(doc, "openTransaction"):
                try:
                    doc.openTransaction("Modify Node Graph")
                    self.doc_object.GraphData = new_json
                    doc.commitTransaction()
                except Exception:
                    self.doc_object.GraphData = new_json
            else:
                self.doc_object.GraphData = new_json

    def sync_from_document_object(self):
        """Sync and re-render editor graph and scene graphics items from doc_object storage."""
        if self.doc_object and hasattr(self.doc_object, "GraphData") and self.doc_object.GraphData:
            try:
                data = json.loads(self.doc_object.GraphData)
                try:
                    self.scene.changed.disconnect(self.save_to_document_object)
                except Exception:
                    pass

                self.graph.clear()
                GraphSerializer.from_dict(data, graph=self.graph)
                self.scene.sync_from_graph()

                self.scene.changed.connect(self.save_to_document_object)
            except Exception:
                pass

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
