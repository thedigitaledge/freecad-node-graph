"""Interactive QGraphicsView for navigating and connecting nodes."""

from PySide6.QtWidgets import QGraphicsView, QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QWheelEvent, QMouseEvent

from typing import Optional
from freecad_nodegraph.gui.items import GraphicsSocketItem, GraphicsNodeItem
from freecad_nodegraph.gui.scene import NodeGraphicsScene


class NodeGraphicsView(QGraphicsView):
    """View widget providing panning, zooming, rubberband selection, and edge drag-connection interaction."""

    def __init__(self, scene: NodeGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.node_scene: NodeGraphicsScene = scene

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)

        self.drag_start_socket_item: Optional[GraphicsSocketItem] = None
        self.temp_edge_item: Optional[QGraphicsPathItem] = None
        self.is_panning: bool = False
        self.pan_start = None

    def keyPressEvent(self, event):
        """Handle key press events (e.g. Del/Backspace to delete selected nodes, Ctrl+Z Undo, Ctrl+Y Redo)."""
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.node_scene and hasattr(self.node_scene, "delete_selected_nodes"):
                self.node_scene.delete_selected_nodes()
                event.accept()
                return

        # Undo: Ctrl+Z
        if event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier):
            if not (event.modifiers() & Qt.ShiftModifier):
                self.handle_undo()
                event.accept()
                return
            else:
                self.handle_redo()
                event.accept()
                return

        # Redo: Ctrl+Y
        if event.key() == Qt.Key_Y and (event.modifiers() & Qt.ControlModifier):
            self.handle_redo()
            event.accept()
            return

        super().keyPressEvent(event)

    def handle_undo(self):
        from freecad_nodegraph.commands import get_active_editor
        editor = get_active_editor()
        if editor and hasattr(editor, "undo"):
            if editor.undo():
                return

        doc = getattr(editor.doc_object, "Document", None) if (editor and hasattr(editor, "doc_object")) else None
        try:
            import FreeCADGui
            if hasattr(FreeCADGui, "runCommand"):
                try:
                    FreeCADGui.runCommand("Std_Undo")
                except Exception:
                    if doc and hasattr(doc, "undo"):
                        doc.undo()
            elif doc and hasattr(doc, "undo"):
                doc.undo()
        except ImportError:
            if doc and hasattr(doc, "undo"):
                doc.undo()

        if editor and hasattr(editor, "sync_from_document_object"):
            editor.sync_from_document_object()

    def handle_redo(self):
        from freecad_nodegraph.commands import get_active_editor
        editor = get_active_editor()
        if editor and hasattr(editor, "redo"):
            if editor.redo():
                return

        doc = getattr(editor.doc_object, "Document", None) if (editor and hasattr(editor, "doc_object")) else None
        try:
            import FreeCADGui
            if hasattr(FreeCADGui, "runCommand"):
                try:
                    FreeCADGui.runCommand("Std_Redo")
                except Exception:
                    if doc and hasattr(doc, "redo"):
                        doc.redo()
            elif doc and hasattr(doc, "redo"):
                doc.redo()
        except ImportError:
            if doc and hasattr(doc, "redo"):
                doc.redo()

        if editor and hasattr(editor, "sync_from_document_object"):
            editor.sync_from_document_object()

    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom in/out with mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        item = self.itemAt(event.pos())

        if event.button() == Qt.RightButton:
            # If right click is on a node item, let QGraphicsView deliver contextMenuEvent
            if isinstance(item, (GraphicsNodeItem, GraphicsSocketItem)) or (
                item and item.parentItem() and isinstance(item.parentItem(), GraphicsNodeItem)
            ):
                super().mousePressEvent(event)
                return

            # Otherwise, right click drag on empty canvas background for view panning
            self.setDragMode(QGraphicsView.NoDrag)
            self.is_panning = True
            self.pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.LeftButton:
            if isinstance(item, GraphicsSocketItem):
                self.drag_start_socket_item = item
                self.temp_edge_item = QGraphicsPathItem()
                pen = QPen(QColor("#FF9800"), 2.0, Qt.DashLine)
                self.temp_edge_item.setPen(pen)
                self.node_scene.addItem(self.temp_edge_item)
                event.accept()
                return

            # Keep RubberBandDrag active for group mouse selection on background
            self.setDragMode(QGraphicsView.RubberBandDrag)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning and self.pan_start:
            delta = event.pos() - self.pan_start
            self.pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        if self.drag_start_socket_item and self.temp_edge_item:
            start_pos = self.drag_start_socket_item.get_scene_pos()
            end_pos = self.mapToScene(event.pos())

            path = QPainterPath(start_pos)
            dx = end_pos.x() - start_pos.x()
            ctrl_offset = max(abs(dx) * 0.5, 40)
            c1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
            c2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())
            path.cubicTo(c1, c2, end_pos)

            self.temp_edge_item.setPath(path)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton and self.is_panning:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
            return

        res = super().mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton and self.drag_start_socket_item:
            if self.temp_edge_item:
                self.node_scene.removeItem(self.temp_edge_item)
                self.temp_edge_item = None

            item = self.itemAt(event.pos())
            if isinstance(item, GraphicsSocketItem) and item != self.drag_start_socket_item:
                start_sock = self.drag_start_socket_item.socket
                end_sock = item.socket
                edge = self.node_scene.graph.connect_sockets(start_sock, end_sock)
                if edge:
                    self.node_scene.add_edge_item(edge)

            self.drag_start_socket_item = None
            event.accept()

        # Trigger save to document object on drag completion
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, "save_to_document_object"):
            parent_widget.save_to_document_object()

        return res
