"""Main Node Graph Editor Widget window, Task Panel, and Model Tab Property Inspector."""

import os
import json
try:
    from PySide6.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTreeWidget,
        QTreeWidgetItem,
        QToolBar,
        QFileDialog,
        QMessageBox,
        QLabel,
        QDoubleSpinBox,
        QLineEdit,
        QFormLayout,
        QGroupBox,
        QPushButton,
        QSplitter,
        QTabWidget,
        QDockWidget,
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QIcon
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QMainWindow,
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QTreeWidget,
            QTreeWidgetItem,
            QToolBar,
            QFileDialog,
            QMessageBox,
            QLabel,
            QDoubleSpinBox,
            QLineEdit,
            QFormLayout,
            QGroupBox,
            QPushButton,
            QSplitter,
            QTabWidget,
            QDockWidget,
        )
        from PySide2.QtCore import Qt, QAction, QIcon
    except ImportError:
        from PyQt5.QtWidgets import (
            QMainWindow,
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QTreeWidget,
            QTreeWidgetItem,
            QToolBar,
            QFileDialog,
            QMessageBox,
            QLabel,
            QDoubleSpinBox,
            QLineEdit,
            QFormLayout,
            QGroupBox,
            QPushButton,
            QAction,
            QSplitter,
            QTabWidget,
            QDockWidget,
        )
        from PyQt5.QtCore import Qt

try:
    import FreeCAD
    import FreeCADGui
    HAS_FREECAD = True
except ImportError:
    HAS_FREECAD = False

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.core.evaluator import GraphEvaluator, EvaluationError
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.workbench_generator import discover_workbench_functions
from freecad_nodegraph.gui.scene import NodeGraphicsScene
from freecad_nodegraph.gui.view import NodeGraphicsView


class NodePropertyInspector(QWidget):
    """Properties Inspector integrated with the base section of FreeCAD's Model tab."""

    def __init__(self, editor_window=None, parent=None):
        super().__init__(parent)
        self.editor_window = None
        self._scene_connected = False
        self.setWindowTitle("Node Property Inspector")
        self.init_ui()

        if editor_window:
            self.set_editor_window(editor_window)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        prop_label = QLabel("<b>Node Properties Inspector</b>")
        layout.addWidget(prop_label)

        self.prop_group = QGroupBox("Selected Node Inputs")
        self.prop_form_layout = QFormLayout(self.prop_group)
        layout.addWidget(self.prop_group)

        layout.addStretch()

    def set_editor_window(self, editor_window):
        """Link editor window and connect scene selection signals cleanly."""
        if self.editor_window == editor_window:
            return
        self.editor_window = editor_window
        if self.editor_window:
            if getattr(self.editor_window, "property_inspector", None) != self:
                self.editor_window.property_inspector = self
            if hasattr(self.editor_window, "scene") and not self._scene_connected:
                self.editor_window.scene.selectionChanged.connect(self.on_selection_changed)
                self._scene_connected = True
                self.on_selection_changed()

    def embed_in_model_tab_base(self):
        """Integrate this property inspector into the base section of FreeCAD's Model tab."""
        if not HAS_FREECAD:
            return False

        try:
            mw = FreeCADGui.getMainWindow() if hasattr(FreeCADGui, "getMainWindow") else None
            if not mw:
                return False

            combo_view = mw.findChild(QWidget, "Combo View") or mw.findChild(QWidget, "ComboView")
            if combo_view:
                splitters = combo_view.findChildren(QSplitter)
                if splitters:
                    splitters[0].addWidget(self)
                    return True

                tabs = combo_view.findChildren(QTabWidget)
                if tabs:
                    model_tab = tabs[0].widget(0)
                    if model_tab and model_tab.layout():
                        model_tab.layout().addWidget(self)
                        return True

            left_docks = [d for d in mw.findChildren(QDockWidget) if mw.dockWidgetArea(d) == Qt.LeftDockWidgetArea]
            if left_docks and left_docks[0].widget():
                w = left_docks[0].widget()
                if w.layout():
                    w.layout().addWidget(self)
                    return True
        except Exception as e:
            if hasattr(FreeCAD, "Console"):
                FreeCAD.Console.PrintWarning(f"NodeGraph: Could not embed Property Inspector in Model tab base: {e}\n")

        return False

    def on_selection_changed(self):
        """Update property inspector controls when selection in active scene changes."""
        while self.prop_form_layout.count():
            child = self.prop_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.editor_window or not hasattr(self.editor_window, "scene"):
            return

        try:
            selected_items = self.editor_window.scene.selectedItems()
        except (AttributeError, RuntimeError):
            return

        if not selected_items:
            self.prop_group.setTitle("Selected Node Inputs")
            return

        item = selected_items[0]
        if hasattr(item, "node"):
            node = item.node
            self.prop_group.setTitle(f"Node: {node.title}")

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
                                if self.editor_window:
                                    self.editor_window.save_to_doc_object()
                            return handler

                        spin.valueChanged.connect(make_change_handler(sock, spin))
                        self.prop_form_layout.addRow(f"{sock.name}:", spin)
                    else:
                        line_edit = QLineEdit(str(sock.default_value or ""))

                        def make_text_handler(s, le):
                            def handler(txt):
                                s.default_value = txt
                                s.node.mark_dirty()
                                if self.editor_window:
                                    self.editor_window.save_to_doc_object()
                            return handler

                        line_edit.textChanged.connect(make_text_handler(sock, line_edit))
                        self.prop_form_layout.addRow(f"{sock.name}:", line_edit)


class NodeGraphTaskPanel(QWidget):
    """Task view panel containing the Node Library with real-time search filter."""

    def __init__(self, editor_window=None, parent=None):
        super().__init__(parent)
        self.editor_window = editor_window
        self.setWindowTitle("NodeGraph Task Panel")
        self.init_ui()

        if editor_window:
            self.set_editor_window(editor_window)

    @property
    def form(self):
        """FreeCAD TaskPanel compatibility attribute returning this widget."""
        return self

    def getStandardButtons(self):
        """FreeCAD TaskPanel compatibility method for standard dialog buttons."""
        return 0

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Search Panel & Node Library
        node_lib_label = QLabel("<b>Node Library</b>")
        layout.addWidget(node_lib_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search nodes...")
        self.search_edit.textChanged.connect(self.filter_nodes)
        layout.addWidget(self.search_edit)

        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderHidden(True)
        self.node_tree.itemDoubleClicked.connect(self.on_node_library_double_clicked)
        layout.addWidget(self.node_tree)

        self.populate_node_library()
        layout.addStretch()

    def set_editor_window(self, editor_window):
        """Link editor window."""
        self.editor_window = editor_window
        if self.editor_window and getattr(self.editor_window, "task_panel", None) != self:
            self.editor_window.task_panel = self

    def populate_node_library(self):
        self.node_tree.clear()
        categories = NodeRegistry.get_nodes_by_category()

        for cat_name, node_classes in sorted(categories.items()):
            cat_item = QTreeWidgetItem(self.node_tree, [cat_name])
            cat_item.setExpanded(True)

            for node_cls in node_classes:
                node_item = QTreeWidgetItem(cat_item, [node_cls.title])
                node_item.setData(0, Qt.UserRole, node_cls.node_type)

    def filter_nodes(self, text: str):
        """Filter node library items in real time based on search query."""
        query = text.strip().lower()

        root = self.node_tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            cat_match = query in cat_item.text(0).lower()
            visible_children = 0

            for j in range(cat_item.childCount()):
                child_item = cat_item.child(j)
                node_match = query in child_item.text(0).lower()

                if cat_match or node_match or not query:
                    child_item.setHidden(False)
                    visible_children += 1
                else:
                    child_item.setHidden(True)

            if visible_children > 0 or not query:
                cat_item.setHidden(False)
                if query:
                    cat_item.setExpanded(True)
            else:
                cat_item.setHidden(True)

    def on_node_library_double_clicked(self, item: QTreeWidgetItem, column: int):
        node_type = item.data(0, Qt.UserRole)
        if node_type and self.editor_window:
            self.editor_window.spawn_node_by_type(node_type)


class NodeGraphEditorWindow(QMainWindow):
    """MDI View tab window for the FreeCAD NodeGraph editor."""

    def __init__(self, graph: Graph = None, parent=None, title: str = "NodeGraph", doc_object=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1000, 700)

        self.doc_object = doc_object
        self.discovered_workbenches = discover_workbench_functions()

        self.graph = graph or Graph()
        self.scene = NodeGraphicsScene(self.graph)
        self.view = NodeGraphicsView(self.scene)

        self.task_panel = None
        self.property_inspector = None

        self.load_from_doc_object()
        self.init_ui()

    def init_ui(self):
        self.setCentralWidget(self.view)
        self.create_main_toolbar()
        self.create_workbench_toolbars()

    def set_task_panel(self, task_panel: NodeGraphTaskPanel):
        """Link task panel."""
        self.task_panel = task_panel
        if self.task_panel:
            self.task_panel.set_editor_window(self)

    def set_property_inspector(self, property_inspector: NodePropertyInspector):
        """Link property inspector."""
        self.property_inspector = property_inspector
        if self.property_inspector:
            self.property_inspector.set_editor_window(self)

    def load_from_doc_object(self):
        """Load graph data from linked document object's GraphData property."""
        if self.doc_object and hasattr(self.doc_object, "GraphData") and self.doc_object.GraphData:
            try:
                data = json.loads(self.doc_object.GraphData)
                if data and isinstance(data, dict) and "nodes" in data:
                    GraphSerializer.deserialize(data, self.graph)
                    self.scene.sync_from_graph()
            except Exception as e:
                print(f"Error loading graph from document object: {e}")

    def save_to_doc_object(self):
        """Save active graph data into linked document object's GraphData property."""
        if self.doc_object and hasattr(self.doc_object, "GraphData"):
            data = GraphSerializer.serialize(self.graph)
            self.doc_object.GraphData = json.dumps(data)

    def create_main_toolbar(self):
        toolbar = QToolBar("NodeGraph Controls", self)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        run_action = QAction("Run Graph", self)
        run_action.setToolTip("Evaluate and update active document")
        run_action.triggered.connect(self.run_graph)
        toolbar.addAction(run_action)

        toolbar.addSeparator()

        clear_action = QAction("Clear Graph", self)
        clear_action.triggered.connect(self.clear_graph)
        toolbar.addAction(clear_action)

        save_action = QAction("Save Graph...", self)
        save_action.triggered.connect(self.save_graph)
        toolbar.addAction(save_action)

        load_action = QAction("Load Graph...", self)
        load_action.triggered.connect(self.load_graph)
        toolbar.addAction(load_action)

    def create_workbench_toolbars(self):
        """Create toolbars with buttons for each workbench's scriptable functions."""
        for wb_name, funcs in sorted(self.discovered_workbenches.items()):
            wb_toolbar = QToolBar(f"{wb_name} Workbench", self)
            self.addToolBar(Qt.TopToolBarArea, wb_toolbar)

            lbl_action = QAction(f"[{wb_name}]", self)
            lbl_action.setEnabled(False)
            wb_toolbar.addAction(lbl_action)

            for func_name, node_cls in sorted(funcs.items()):
                clean_name = func_name.replace("make_", "").replace("make", "").strip("_")
                btn_title = clean_name[0].upper() + clean_name[1:] if clean_name else func_name

                action = QAction(btn_title, self)
                action.setToolTip(f"Spawn {wb_name}.{func_name} node")

                def make_spawn_handler(ntype):
                    def handler():
                        self.spawn_node_by_type(ntype)
                    return handler

                action.triggered.connect(make_spawn_handler(node_cls.node_type))
                wb_toolbar.addAction(action)

    def spawn_node_by_type(self, node_type: str):
        """Instantiate and add a node to the canvas near the view center."""
        node = NodeRegistry.create_node(node_type, graph=self.graph)
        if node:
            view_center = self.view.mapToScene(self.view.viewport().rect().center())
            node.pos_x = view_center.x() - 80
            node.pos_y = view_center.y() - 50

            self.graph.add_node(node)
            self.scene.add_node_item(node)
            self.save_to_doc_object()

    def run_graph(self):
        evaluator = GraphEvaluator(self.graph)
        try:
            evaluated = evaluator.evaluate(force=True)
            QMessageBox.information(
                self,
                "NodeGraph Evaluation",
                f"Successfully evaluated {len(evaluated)} nodes in graph.",
            )
        except EvaluationError as e:
            QMessageBox.critical(self, "Evaluation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Execution Error", f"Failed: {str(e)}")

    def clear_graph(self):
        self.graph.clear()
        self.scene.sync_from_graph()
        self.save_to_doc_object()

    def save_graph(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save NodeGraph", "", "JSON Graph Files (*.json)"
        )
        if filepath:
            GraphSerializer.save_to_file(self.graph, filepath)
            QMessageBox.information(self, "Saved", f"Graph saved to {filepath}")

    def load_graph(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open NodeGraph", "", "JSON Graph Files (*.json)"
        )
        if filepath and os.path.exists(filepath):
            GraphSerializer.load_from_file(filepath, self.graph)
            self.scene.sync_from_graph()
            self.save_to_doc_object()
            QMessageBox.information(self, "Loaded", f"Graph loaded from {filepath}")
