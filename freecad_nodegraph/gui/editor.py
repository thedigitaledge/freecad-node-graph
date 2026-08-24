"""Main Node Graph Editor View widget (MDI window bound to a specific graph data storage)."""

import json
try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
    )
    from PySide6.QtCore import Qt, QEvent
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
        )
        from PySide2.QtCore import Qt, QEvent
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
        )
        from PyQt5.QtCore import Qt, QEvent

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView

# Optional callback triggered when NodeGraph editor is activated/focused
_on_editor_activated_callback = None


def set_editor_activated_callback(callback):
    """Set global callback to invoke when a NodeGraphEditorWidget is activated/focused."""
    global _on_editor_activated_callback
    _on_editor_activated_callback = callback


class NodeGraphEditorWidget(QWidget):
    """Main application view widget for the FreeCAD NodeGraph editor (bound to an individual Document Object storage)."""

    def __init__(self, graph: Graph = None, doc_object=None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphEditorWidget")
        self.doc_object = doc_object

        title_name = getattr(doc_object, "Label", getattr(doc_object, "Name", "NodeGraph"))
        self.setWindowTitle(f"NodeGraph - {title_name}")

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
            self.doc_object.GraphData = json.dumps(data)

    def changeEvent(self, event):
        """Trigger activation callback when view window is activated."""
        if event.type() in (QEvent.ActivationChange, QEvent.WindowStateChange):
            if self.isActiveWindow():
                self.on_activated()
        super().changeEvent(event)

    def focusInEvent(self, event):
        """Trigger activation callback when view receives focus."""
        self.on_activated()
        super().focusInEvent(event)

    def mousePressEvent(self, event):
        """Trigger activation callback when view is clicked."""
        self.on_activated()
        super().mousePressEvent(event)

    def on_activated(self):
        """Invoke editor activation callback to show Node Library view tab."""
        global _on_editor_activated_callback
        if callable(_on_editor_activated_callback):
            _on_editor_activated_callback(self)


# Alias for compatibility
NodeGraphEditorWindow = NodeGraphEditorWidget
