"""Side Panel widget and FreeCAD TaskPanel for Node Library and Properties Inspector."""

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
            QPushButton,
        )
        from PyQt5.QtCore import Qt

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.workbench_generator import discover_workbench_functions


class NodeGraphSidePanelWidget(QWidget):
    """Side panel widget containing Node Library with Real-time Search and Properties Inspector."""

    def __init__(self, graph: Graph = None, parent=None):
        super().__init__(parent)
        self.setObjectName("NodeGraphSidePanelWidget")
        self.setWindowTitle("Node Library")

        self.graph = graph or Graph()
        self.discovered_workbenches = discover_workbench_functions()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
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
        layout.addWidget(self.node_tree)

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

    def on_node_library_double_clicked(self, item: QTreeWidgetItem, column: int):
        node_type = item.data(0, Qt.UserRole)
        if node_type:
            node = NodeRegistry.create_node(node_type, graph=self.graph)
            if node:
                self.graph.add_node(node)


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
