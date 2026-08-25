"""QGraphicsItem representations for Sockets, Edges, and Nodes."""

import sys
try:
    from PySide6.QtWidgets import (
        QGraphicsItem,
        QGraphicsTextItem,
        QGraphicsPathItem,
        QGraphicsDropShadowEffect,
        QStyleOptionGraphicsItem,
        QGraphicsProxyWidget,
        QDoubleSpinBox,
        QSpinBox,
        QLineEdit,
        QCheckBox,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QMenu,
    )
    from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
    from PySide6.QtGui import (
        QPen,
        QBrush,
        QColor,
        QPainter,
        QPainterPath,
        QFont,
        QLinearGradient,
        QAction,
        QCursor,
    )
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QWidget,
            QMenu,
        )
        from PySide2.QtCore import Qt, QPointF, QRectF, QPoint
        from PySide2.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
            QAction,
            QCursor,
        )
    except ImportError:
        from PyQt5.QtWidgets import (
            QGraphicsItem,
            QGraphicsTextItem,
            QGraphicsPathItem,
            QGraphicsDropShadowEffect,
            QStyleOptionGraphicsItem,
            QGraphicsProxyWidget,
            QDoubleSpinBox,
            QSpinBox,
            QLineEdit,
            QCheckBox,
            QLabel,
            QHBoxLayout,
            QVBoxLayout,
            QWidget,
            QMenu,
            QAction,
        )
        from PyQt5.QtCore import Qt, QPointF, QRectF, QPoint
        from PyQt5.QtGui import (
            QPen,
            QBrush,
            QColor,
            QPainter,
            QPainterPath,
            QFont,
            QLinearGradient,
            QCursor,
        )

from typing import TYPE_CHECKING, Optional
from freecad_nodegraph.core.socket import DataType

if TYPE_CHECKING:
    from freecad_nodegraph.core.socket import Socket
    from freecad_nodegraph.core.node import BaseNode
    from freecad_nodegraph.core.edge import Edge

# Color palette mapping for DataType
SOCKET_TYPE_COLORS = {
    DataType.FLOAT: QColor("#A6E22E"),      # Lime Green
    DataType.INT: QColor("#66D9EF"),        # Cyan
    DataType.STRING: QColor("#E6DB74"),     # Yellow
    DataType.BOOLEAN: QColor("#AE81FF"),    # Purple
    DataType.VECTOR: QColor("#FD971F"),     # Orange
    DataType.PLACEMENT: QColor("#F92672"),  # Pink / Magenta
    DataType.SHAPE: QColor("#2196F3"),      # Blue
    DataType.OBJECT: QColor("#00ACC1"),     # Teal
    DataType.ANY: QColor("#B0BEC5"),        # Light Gray
}


class GraphicsSocketItem(QGraphicsItem):
    """Visual graphics item for a node socket."""

    def __init__(self, socket: "Socket", parent: "GraphicsNodeItem"):
        super().__init__(parent)
        self.socket = socket
        self.node_item = parent
        self.radius = 6.5

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{self.socket.name} ({self.socket.data_type.value})")

    def get_color(self) -> QColor:
        return SOCKET_TYPE_COLORS.get(self.socket.data_type, QColor("#B0BEC5"))

    def boundingRect(self) -> QRectF:
        r = self.radius + 4
        return QRectF(-r, -r, 2 * r, 2 * r)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.get_color()
        if self.socket.is_connected:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        else:
            painter.setBrush(QBrush(QColor("#222222")))
            painter.setPen(QPen(color, 2.0))

        painter.drawEllipse(
            QPointF(0, 0), self.radius, self.radius
        )

    def get_scene_pos(self) -> QPointF:
        return self.scenePos()


class GraphicsEdgeItem(QGraphicsPathItem):
    """Visual graphics item for a connection edge."""

    def __init__(self, edge: "Edge", parent=None):
        super().__init__(parent)
        self.edge = edge
        self.setZValue(-1)

        self.pen = QPen(QColor("#FF9800"), 2.5, Qt.SolidLine)
        self.pen.setCapStyle(Qt.RoundCap)
        self.setPen(self.pen)

    def update_path(self, start_pos: QPointF = None, end_pos: QPointF = None):
        if not start_pos or not end_pos:
            if not self.edge.start_socket or not self.edge.end_socket:
                return

            scene = self.scene()
            if not scene:
                return

            start_item = scene.get_socket_item(self.edge.start_socket)
            end_item = scene.get_socket_item(self.edge.end_socket)

            if not start_item or not end_item:
                return

            start_pos = start_item.get_scene_pos()
            end_pos = end_item.get_scene_pos()

            # Dynamic edge color matching start socket type
            color = start_item.get_color()
            self.pen.setColor(color)
            self.setPen(self.pen)

        path = QPainterPath(start_pos)
        dx = end_pos.x() - start_pos.x()

        ctrl_offset = max(abs(dx) * 0.5, 40)

        c1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
        c2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())

        path.cubicTo(c1, c2, end_pos)
        self.setPath(path)


class GraphicsNodeItem(QGraphicsItem):
    """Visual graphics item for a node."""

    def __init__(self, node: "BaseNode"):
        super().__init__()
        self.node = node
        self.width = 180.0
        self.height = 100.0

        self.socket_items = {}
        self.label_items = []

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        self.init_ui()

    def init_ui(self):
        self.setPos(self.node.pos_x, self.node.pos_y)

        # Title text item
        self.title_item = QGraphicsTextItem(self.node.title, self)
        self.title_item.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Arial", 10, QFont.Bold)
        self.title_item.setFont(font)
        self.title_item.setPos(10, 5)

        self.recalculate_size()
        self.create_sockets()
        self.create_input_widgets()

    def recalculate_size(self):
        num_inputs = len(self.node.inputs)
        num_outputs = len(self.node.outputs)
        max_socks = max(num_inputs, num_outputs, 1)

        self.height = 35 + max_socks * 24 + 10

        # Calculate width needed for longest socket labels
        max_in_len = max([len(s.name) for s in self.node.inputs] or [0])
        max_out_len = max([len(s.name) for s in self.node.outputs] or [0])
        title_len = len(self.node.title)

        calculated_width = max(180.0, (max_in_len + max_out_len + 4) * 8.0, title_len * 9.0)
        self.width = calculated_width

        cat = getattr(self.node, "category", "")
        node_type = getattr(self.node, "node_type", self.node.__class__.__name__)
        if cat == "Input":
            if node_type in ("VectorNode", "PlacementNode"):
                self.height = max(self.height, 135.0)
                self.width = max(self.width, 200.0)
            else:
                self.height = max(self.height, 80.0)
                self.width = max(self.width, 180.0)

    def create_input_widgets(self):
        cat = getattr(self.node, "category", "")
        node_type = getattr(self.node, "node_type", self.node.__class__.__name__)

        if cat != "Input":
            return

        proxy = QGraphicsProxyWidget(self)
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        if node_type == "FloatNode":
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            spin = QDoubleSpinBox()
            spin.setRange(-999999.0, 999999.0)
            spin.setDecimals(3)
            spin.setValue(float(getattr(self.node, "value", 0.0)))

            def on_float_changed(val):
                try:
                    self.node.set_value(val)
                    spin.setStyleSheet("")
                except ValueError:
                    spin.setStyleSheet("border: 1px solid red;")

            spin.valueChanged.connect(on_float_changed)
            layout.addWidget(spin)
            proxy.setWidget(container)
            proxy.setPos(5, 38)

        elif node_type == "IntegerNode":
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            spin = QSpinBox()
            spin.setRange(-999999, 999999)
            spin.setValue(int(getattr(self.node, "value", 0)))

            def on_int_changed(val):
                try:
                    self.node.set_value(val)
                    spin.setStyleSheet("")
                except ValueError:
                    spin.setStyleSheet("border: 1px solid red;")

            spin.valueChanged.connect(on_int_changed)
            layout.addWidget(spin)
            proxy.setWidget(container)
            proxy.setPos(5, 38)

        elif node_type == "StringNode":
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            edit = QLineEdit(str(getattr(self.node, "value", "")))

            def on_string_changed(txt):
                self.node.set_value(txt)

            edit.textChanged.connect(on_string_changed)
            layout.addWidget(edit)
            proxy.setWidget(container)
            proxy.setPos(5, 38)

        elif node_type == "BooleanNode":
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            chk = QCheckBox("True")
            chk.setChecked(bool(getattr(self.node, "value", False)))
            chk.setStyleSheet("color: white;")

            def on_bool_changed(state):
                self.node.set_value(bool(state))

            chk.stateChanged.connect(on_bool_changed)
            layout.addWidget(chk)
            proxy.setWidget(container)
            proxy.setPos(5, 38)

        elif node_type == "VectorNode":
            layout = QVBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            layout.setSpacing(2)

            for comp, label_text in [("x", "X:"), ("y", "Y:"), ("z", "Z:")]:
                h_layout = QHBoxLayout()
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: white; font-weight: bold;")
                spin = QDoubleSpinBox()
                spin.setRange(-999999.0, 999999.0)
                spin.setDecimals(3)
                spin.setValue(float(getattr(self.node, comp, 0.0)))

                def make_vec_handler(c_name, sp):
                    def handler(val):
                        try:
                            self.node.set_components(**{c_name: val})
                            sp.setStyleSheet("")
                        except ValueError:
                            sp.setStyleSheet("border: 1px solid red;")
                    return handler

                spin.valueChanged.connect(make_vec_handler(comp, spin))
                h_layout.addWidget(lbl)
                h_layout.addWidget(spin)
                layout.addLayout(h_layout)

            proxy.setWidget(container)
            proxy.setPos(5, 38)

        elif node_type == "PlacementNode":
            layout = QVBoxLayout(container)
            layout.setContentsMargins(10, 0, 10, 0)
            layout.setSpacing(2)

            for comp, label_text in [("x", "X:"), ("y", "Y:"), ("z", "Z:")]:
                h_layout = QHBoxLayout()
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: white; font-weight: bold;")
                spin = QDoubleSpinBox()
                spin.setRange(-999999.0, 999999.0)
                spin.setDecimals(3)
                pos_val = getattr(self.node, f"pos_{comp}", 0.0)
                spin.setValue(float(pos_val))

                def make_pos_handler(c_name, sp):
                    def handler(val):
                        try:
                            self.node.set_position(**{c_name: val})
                            sp.setStyleSheet("")
                        except ValueError:
                            sp.setStyleSheet("border: 1px solid red;")
                    return handler

                spin.valueChanged.connect(make_pos_handler(comp, spin))
                h_layout.addWidget(lbl)
                h_layout.addWidget(spin)
                layout.addLayout(h_layout)

            proxy.setWidget(container)
            proxy.setPos(5, 38)

    def create_sockets(self):
        label_font = QFont("Arial", 8, QFont.Bold)

        # Input Sockets and Labels
        for i, sock in enumerate(self.node.inputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(0, y_pos)
            self.socket_items[sock] = item

            # Input socket text label
            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#E0E0E0"))
            txt.setFont(label_font)
            txt.setPos(12, y_pos - 10)
            self.label_items.append(txt)

        # Output Sockets and Labels
        for i, sock in enumerate(self.node.outputs):
            item = GraphicsSocketItem(sock, self)
            y_pos = 40 + i * 24
            item.setPos(self.width, y_pos)
            self.socket_items[sock] = item

            # Output socket text label
            txt = QGraphicsTextItem(sock.name, self)
            txt.setDefaultTextColor(QColor("#E0E0E0"))
            txt.setFont(label_font)
            txt.setPos(self.width - txt.boundingRect().width() - 12, y_pos - 10)
            self.label_items.append(txt)

    def contextMenuEvent(self, event):
        """Handle secondary (right-click) context menu on node."""
        menu = QMenu()

        cut_act = menu.addAction("Cut")
        copy_act = menu.addAction("Copy")
        paste_act = menu.addAction("Paste")
        duplicate_act = menu.addAction("Duplicate")
        menu.addSeparator()
        detach_act = menu.addAction("Detach Links")

        scene = self.scene()
        if not scene or not hasattr(scene, "clipboard_data"):
            paste_act.setEnabled(False)
        elif not scene.clipboard_data:
            paste_act.setEnabled(False)

        pos = event.screenPos().toPoint() if hasattr(event.screenPos(), "toPoint") else QCursor.pos()
        selected_action = menu.exec_(pos)

        if selected_action == cut_act:
            if scene and hasattr(scene, "cut_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.cut_selected_nodes()
        elif selected_action == copy_act:
            if scene and hasattr(scene, "copy_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.copy_selected_nodes()
        elif selected_action == paste_act:
            if scene and hasattr(scene, "paste_nodes"):
                scene.paste_nodes()
        elif selected_action == duplicate_act:
            if scene and hasattr(scene, "duplicate_selected_nodes"):
                if not self.isSelected():
                    self.setSelected(True)
                scene.duplicate_selected_nodes()
        elif selected_action == detach_act:
            if scene and hasattr(scene, "detach_node_links"):
                scene.detach_node_links(self.node)

        event.accept()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        # Body rectangle
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)

        # Background color
        body_color = QColor("#353535")
        if self.isSelected():
            pen_color = QColor("#FFA726")
            pen_width = 2.5
        else:
            pen_color = QColor("#555555")
            pen_width = 1.5

        painter.setPen(QPen(pen_color, pen_width))
        painter.setBrush(QBrush(body_color))
        painter.drawPath(path)

        # Header bar
        header_path = QPainterPath()
        header_path.addRoundedRect(0, 0, self.width, 30, 8, 8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#252525")))
        painter.drawPath(header_path)

        # Divider line
        painter.setPen(QPen(QColor("#555555"), 1.0))
        painter.drawLine(0, 30, self.width, 30)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.node.pos_x = value.x()
            self.node.pos_y = value.y()
            if self.scene():
                self.scene().update_node_edges(self)
        return super().itemChange(change, value)
