"""Side Panel widget containing Node Library with Search feature and Properties Inspector."""

import os
try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLineEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QGroupBox,
        QFormLayout,
        QLabel,
        QDoubleSpinBox,
        QCheckBox,
        QPushButton,
    )
    from PySide6.QtCore import Qt
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QLineEdit,
            QTreeWidget,
            QTreeWidgetItem,
            QGroupBox,
            QFormLayout,
            QLabel,
            QDoubleSpinBox,
            QCheckBox,
            QPushButton,
        )
        from PySide2.QtCore import Qt
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QLineEdit,
            QTreeWidget,
            QTreeWidgetItem,
            QGroupBox,
            QFormLayout,
            QLabel,
            QDoubleSpinBox,
            QCheckBox,
            QPushButton,
        )
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.workbench_generator import discover_workbench_functions


class NodeGraphSidePanelWidget(QWidget):
    """Overlay side panel widget containing Node Library with Real-time Search and Properties Inspector."""

    def __init__(self, graph: Graph = None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphSidePanelWidget")
        self.setWindowTitle("Node Library")

        self.graph = graph or Graph()
        self.discovered_workbenches = discover_workbench_functions()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 1. Search Bar Input
        search_box = QWidget()
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter nodes by name...")
        self.search_input.textChanged.connect(self.filter_node_library)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_box)

        # 2. Node Library Tree
        node_lib_label = QLabel("<b>Node Palette</b>")
        layout.addWidget(node_lib_label)

        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderHidden(True)
        self.node_tree.itemDoubleClicked.connect(self.on_node_library_double_clicked)
        self.node_tree.itemActivated.connect(self.on_node_library_double_clicked)
        layout.addWidget(self.node_tree)

        self.add_node_btn = QPushButton("Add Node to Active Graph")
        self.add_node_btn.clicked.connect(self.on_add_node_button_clicked)
        layout.addWidget(self.add_node_btn)

        self.populate_node_library()

        # 3. Properties Inspector
        self.prop_group = QGroupBox("Selected Node Inputs")
        self.prop_form_layout = QFormLayout(self.prop_group)
        layout.addWidget(self.prop_group)

        layout.addStretch()

    def populate_node_library(self):
        self.node_tree.clear()
        categories = NodeRegistry.get_nodes_by_category()

        for cat_name, node_classes in sorted(categories.items()):
            cat_item = QTreeWidgetItem(self.node_tree, [cat_name])
            cat_item.setExpanded(True)

            for node_cls in node_classes:
                node_item = QTreeWidgetItem(cat_item, [node_cls.title])
                node_item.setData(0, Qt.UserRole, node_cls.node_type)

    def filter_node_library(self, text: str):
        """Filter node tree items in real-time based on search input query."""
        search_text = text.lower().strip()

        root = self.node_tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            category_has_match = False

            for j in range(category_item.childCount()):
                child_item = category_item.child(j)
                title = child_item.text(0).lower()
                node_type = (child_item.data(0, Qt.UserRole) or "").lower()

                if not search_text or (search_text in title or search_text in node_type):
                    child_item.setHidden(False)
                    category_has_match = True
                else:
                    child_item.setHidden(True)

            category_item.setHidden(not category_has_match)
            if search_text and category_has_match:
                category_item.setExpanded(True)

    def add_node_from_item(self, item: QTreeWidgetItem):
        if not item:
            return
        node_type = item.data(0, Qt.UserRole)
        if not node_type:
            return

        from freecad_nodegraph.commands import get_active_editor

        editor = get_active_editor()
        if editor is not None and hasattr(editor, "graph") and hasattr(editor, "scene"):
            target_graph = editor.graph
            target_scene = editor.scene
        else:
            target_graph = self.graph
            target_scene = getattr(self, "scene", None)

        node = NodeRegistry.create_node(node_type, graph=target_graph)
        if node:
            target_graph.add_node(node)
            if target_scene is not None and hasattr(target_scene, "add_node_item"):
                target_scene.add_node_item(node)
            if editor is not None and hasattr(editor, "save_to_document_object"):
                editor.save_to_document_object()

    def on_node_library_double_clicked(self, item: QTreeWidgetItem, column: int = 0):
        self.add_node_from_item(item)

    def on_add_node_button_clicked(self):
        curr_item = self.node_tree.currentItem()
        if curr_item:
            self.add_node_from_item(curr_item)

    def update_properties_inspector(self, selected_items):
        """Update property inspector form fields for selected scene items."""
        while self.prop_form_layout.count():
            child = self.prop_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not selected_items:
            self.prop_group.setTitle("Selected Node Inputs")
            return

        item = selected_items[0]
        if hasattr(item, "node"):
            node = item.node
            self.prop_group.setTitle(f"Node: {node.title}")

            cat = getattr(node, "category", "")
            node_type = getattr(node, "node_type", node.__class__.__name__)

            if cat == "Input":
                if node_type == "FloatNode":
                    spin = QDoubleSpinBox()
                    spin.setRange(-999999.0, 999999.0)
                    spin.setDecimals(3)
                    spin.setValue(float(getattr(node, "value", 0.0)))

                    def on_val_changed(val):
                        try:
                            node.set_value(val)
                            spin.setStyleSheet("")
                        except ValueError:
                            spin.setStyleSheet("border: 1px solid red;")

                    spin.valueChanged.connect(on_val_changed)
                    self.prop_form_layout.addRow("Value:", spin)

                elif node_type == "IntegerNode":
                    spin = QDoubleSpinBox()
                    spin.setRange(-999999.0, 999999.0)
                    spin.setDecimals(0)
                    spin.setValue(float(getattr(node, "value", 0)))

                    def on_int_changed(val):
                        try:
                            node.set_value(int(val))
                            spin.setStyleSheet("")
                        except ValueError:
                            spin.setStyleSheet("border: 1px solid red;")

                    spin.valueChanged.connect(on_int_changed)
                    self.prop_form_layout.addRow("Value:", spin)

                elif node_type == "StringNode":
                    edit = QLineEdit(str(getattr(node, "value", "")))

                    def on_str_changed(txt):
                        node.set_value(txt)

                    edit.textChanged.connect(on_str_changed)
                    self.prop_form_layout.addRow("Value:", edit)

                elif node_type == "BooleanNode":
                    chk = QCheckBox("True")
                    chk.setChecked(bool(getattr(node, "value", False)))

                    def on_chk_changed(state):
                        node.set_value(bool(state))

                    chk.stateChanged.connect(on_chk_changed)
                    self.prop_form_layout.addRow("Value:", chk)

                elif node_type == "VectorNode":
                    for comp in ("x", "y", "z"):
                        spin = QDoubleSpinBox()
                        spin.setRange(-999999.0, 999999.0)
                        spin.setDecimals(3)
                        spin.setValue(float(getattr(node, comp, 0.0)))

                        def make_vec_handler(c_name, sp):
                            def handler(val):
                                try:
                                    node.set_components(**{c_name: val})
                                    sp.setStyleSheet("")
                                except ValueError:
                                    sp.setStyleSheet("border: 1px solid red;")
                            return handler

                        spin.valueChanged.connect(make_vec_handler(comp, spin))
                        self.prop_form_layout.addRow(f"Component {comp.upper()}:", spin)

                elif node_type == "PlacementNode":
                    for comp in ("x", "y", "z"):
                        spin = QDoubleSpinBox()
                        spin.setRange(-999999.0, 999999.0)
                        spin.setDecimals(3)
                        spin.setValue(float(getattr(node, f"pos_{comp}", 0.0)))

                        def make_pos_handler(c_name, sp):
                            def handler(val):
                                try:
                                    node.set_position(**{c_name: val})
                                    sp.setStyleSheet("")
                                except ValueError:
                                    sp.setStyleSheet("border: 1px solid red;")
                            return handler

                        spin.valueChanged.connect(make_pos_handler(comp, spin))
                        self.prop_form_layout.addRow(f"Position {comp.upper()}:", spin)

            for sock in node.inputs:
                if sock.is_connected:
                    lbl = QLabel("(Connected)")
                    lbl.setStyleSheet("color: gray;")
                    self.prop_form_layout.addRow(f"{sock.name}:", lbl)
                else:
                    if isinstance(sock.default_value, (int, float)):
                        spin = QDoubleSpinBox()
                        spin.setRange(-999999.0, 999999.0)
                        spin.setDecimals(3)
                        spin.setValue(float(sock.default_value or 0.0))

                        def make_change_handler(s, sp):
                            def handler(val):
                                s.default_value = val
                                s.node.mark_dirty()
                            return handler

                        spin.valueChanged.connect(make_change_handler(sock, spin))
                        self.prop_form_layout.addRow(f"{sock.name}:", spin)
                    else:
                        line_edit = QLineEdit(str(sock.default_value or ""))

                        def make_text_handler(s, le):
                            def handler(txt):
                                s.default_value = txt
                                s.node.mark_dirty()
                            return handler

                        line_edit.textChanged.connect(make_text_handler(sock, line_edit))
                        self.prop_form_layout.addRow(f"{sock.name}:", line_edit)


class NodeGraphTaskPanel:
    """FreeCAD TaskPanel displaying Node Library inside FreeCAD's Tasks view."""

    def __init__(self, graph: Graph = None):
        self.widget = NodeGraphSidePanelWidget(graph=graph)
        self.form = [self.widget]

    def getStandardButtons(self):
        return 0

    def isAllowedAlterDocument(self):
        return True

    def accept(self):
        return True

    def reject(self):
        return True
