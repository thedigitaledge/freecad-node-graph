"""Main Node Graph Editor View widget (MDI window without toolbars)."""

try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
    )
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
        )
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
        )
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView


class NodeGraphEditorWidget(QWidget):
    """Main application view widget for the FreeCAD NodeGraph editor (FreeCAD MDI view)."""

    def __init__(self, graph: Graph = None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphEditorWidget")
        self.setWindowTitle("NodeGraph")

        self.graph = graph or Graph()
        self.scene = NodeGraphicsScene(self.graph)
        self.view = NodeGraphicsView(self.scene)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Pure MDI view canvas (toolbars removed per user request, matching Spreadsheet style)
        root_layout.addWidget(self.view)


# Alias for compatibility
NodeGraphEditorWindow = NodeGraphEditorWidget
