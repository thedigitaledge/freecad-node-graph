"""Main Node Graph Editor View widget with right-side overlay panel."""

import json
try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QSplitter,
        QPushButton,
        QFrame,
    )
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QSplitter,
            QPushButton,
            QFrame,
        )
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QSplitter,
            QPushButton,
            QFrame,
        )
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView
from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget


class NodeGraphEditorWidget(QWidget):
    """Main application view widget for the FreeCAD NodeGraph editor with right-side overlay panel."""

    def __init__(self, graph: Graph = None, doc_object=None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphEditorWidget")
        self.doc_object = doc_object

        title_name = getattr(doc_object, "Label", getattr(doc_object, "Name", "NodeGraph"))
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
        self.side_panel = NodeGraphSidePanelWidget(graph=self.graph)

        # Sync selection between scene and side panel inspector
        self.scene.selectionChanged.connect(self.on_selection_changed)

        # Listen for scene graph changes to automatically save back to doc_object storage
        self.scene.changed.connect(self.save_to_document_object)

        self.init_ui()

    def init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Splitter with Canvas View on Left and Overlay Side Panel on Right
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.side_panel)

        # Initial ratio: Canvas occupies majority, right overlay panel occupies right side (~260px)
        self.splitter.setSizes([900, 260])

        root_layout.addWidget(self.splitter)

    def on_selection_changed(self):
        """Update property inspector in right-side overlay panel when selection changes."""
        selected_items = self.scene.selectedItems()
        if hasattr(self.side_panel, "update_properties_inspector"):
            self.side_panel.update_properties_inspector(selected_items)

    def save_to_document_object(self, *args):
        """Save current graph state back into the bound FreeCAD Document Object property."""
        if self.doc_object and hasattr(self.doc_object, "GraphData"):
            data = GraphSerializer.to_dict(self.graph)
            self.doc_object.GraphData = json.dumps(data)


# Alias for compatibility
NodeGraphEditorWindow = NodeGraphEditorWidget
