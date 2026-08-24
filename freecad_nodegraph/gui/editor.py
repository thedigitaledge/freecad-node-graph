"""Main Node Graph Editor View widget (MDI window without toolbars)."""

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
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView

# Optional callback triggered when NodeGraph editor is activated/focused
_on_editor_activated_callback = None


def set_editor_activated_callback(callback):
    """Set global callback to invoke when a NodeGraphEditorWidget is activated/focused."""
    global _on_editor_activated_callback
    _on_editor_activated_callback = callback


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
