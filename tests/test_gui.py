"""Unit tests for NodeGraph GUI components in offscreen/qapp context."""

import pytest
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsProxyWidget,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtTest import QTest

from freecad_nodegraph.core.socket import DataType
from tests.mocks import MockDocumentObject

# Ensure QApplication instance exists for GUI tests
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_gui_creation(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget, NodeGraphTaskPanel

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)

    scene = NodeGraphicsScene(graph)
    assert len(scene.node_items) == 2

    view = NodeGraphicsView(scene)
    assert view is not None
    assert view.dragMode() == QGraphicsView.RubberBandDrag

    editor = NodeGraphEditorWidget(graph=graph)
    assert editor is not None

    panel = NodeGraphSidePanelWidget(graph=graph)
    assert panel is not None

    task_panel = NodeGraphTaskPanel(graph=graph)
    assert task_panel.widget is not None
    assert len(task_panel.form) == 1


def test_multi_node_selection_and_deletion(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode, IntegerNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView

    graph = Graph()
    f1 = FloatNode(graph=graph)
    f2 = IntegerNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(f2)
    graph.add_node(box)

    scene = NodeGraphicsScene(graph)
    view = NodeGraphicsView(scene)

    assert len(scene.node_items) == 3

    # Select single node
    scene.clearSelection()
    item_f1 = scene.node_items[f1]
    item_f1.setSelected(True)
    assert len(scene.selectedItems()) == 1

    # Select multiple nodes simultaneously
    item_f2 = scene.node_items[f2]
    item_box = scene.node_items[box]

    item_f2.setSelected(True)
    item_box.setSelected(True)
    assert len(scene.selectedItems()) == 3

    # Simultaneous deletion of multiple selected nodes
    scene.delete_selected_nodes()
    assert len(graph.nodes) == 0
    assert len(scene.node_items) == 0


def test_socket_colors_and_labels(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.items import GraphicsNodeItem, SOCKET_TYPE_COLORS

    graph = Graph()
    box = BoxNode(graph=graph)
    graph.add_node(box)

    node_item = GraphicsNodeItem(box)

    # Verify label items were created for each input and output socket
    assert len(node_item.label_items) == len(box.inputs) + len(box.outputs)

    # Check socket colors match DataType mapping
    length_sock = box.get_input_socket("Length")
    sock_item = node_item.socket_items[length_sock]
    assert sock_item.get_color() == SOCKET_TYPE_COLORS[DataType.FLOAT]

    shape_sock = box.get_output_socket("Shape")
    shape_item = node_item.socket_items[shape_sock]
    assert shape_item.get_color() == SOCKET_TYPE_COLORS[DataType.SHAPE]


def test_side_panel_node_search(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget

    graph = Graph()
    panel = NodeGraphSidePanelWidget(graph=graph)

    # Initial state: no search filter
    root = panel.node_tree.invisibleRootItem()
    assert root.childCount() > 0

    # Filter for 'box'
    panel.search_input.setText("box")
    panel.filter_node_library("box")

    # Find Box node item
    found_box = False
    for i in range(root.childCount()):
        cat_item = root.child(i)
        if not cat_item.isHidden():
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if not child.isHidden() and "box" in child.text(0).lower():
                    found_box = True

    assert found_box is True


def test_detach_links(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)

    edge = graph.connect_sockets(f1.get_output_socket("Value"), box.get_input_socket("Length"))
    scene = NodeGraphicsScene(graph)
    assert len(scene.edge_items) == 1

    scene.detach_node_links(box)
    assert len(graph.edges) == 0
    assert len(scene.edge_items) == 0


def test_double_click_creates_single_node(qapp):
    from freecad_nodegraph.commands import _active_editors
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget

    _active_editors.clear()

    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)
    editor.show()
    _active_editors[obj] = (editor, editor)

    panel = NodeGraphSidePanelWidget(graph=editor.graph)

    root = panel.node_tree.invisibleRootItem()
    box_tree_item = None
    for i in range(root.childCount()):
        cat = root.child(i)
        for j in range(cat.childCount()):
            child = cat.child(j)
            if child.data(0, 0x0100) == "BoxNode":
                box_tree_item = child
                break

    assert box_tree_item is not None

    panel.on_node_library_double_clicked(box_tree_item)

    assert len(editor.graph.nodes) == 1
    assert len(editor.scene.node_items) == 1

    _active_editors.clear()


def test_add_node_from_library_to_active_editor(qapp):
    from freecad_nodegraph.commands import _active_editors, get_active_editor
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget

    _active_editors.clear()

    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)
    editor.show()

    # Register in active editors
    _active_editors[obj] = (editor, editor)

    assert get_active_editor() == editor

    panel = NodeGraphSidePanelWidget(graph=editor.graph)

    # Find BoxNode item in library tree
    root = panel.node_tree.invisibleRootItem()
    box_tree_item = None
    for i in range(root.childCount()):
        cat = root.child(i)
        for j in range(cat.childCount()):
            child = cat.child(j)
            if child.data(0, 0x0100) == "BoxNode":  # Qt.UserRole
                box_tree_item = child
                break

    assert box_tree_item is not None

    panel.add_node_from_item(box_tree_item)

    assert len(editor.graph.nodes) == 1
    assert len(editor.scene.node_items) == 1

    # Cleanup
    _active_editors.clear()


def test_input_node_value_entry_and_validation(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode, IntegerNode, VectorNode
    from freecad_nodegraph.gui.items import GraphicsNodeItem
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget

    graph = Graph()

    # 1. FloatNode
    f_node = FloatNode(graph=graph)
    graph.add_node(f_node)
    f_item = GraphicsNodeItem(f_node)
    f_node.set_value(42.5)
    assert f_node.value == 42.5

    with pytest.raises(ValueError):
        f_node.set_value("invalid_float")

    # 2. IntegerNode
    i_node = IntegerNode(graph=graph)
    graph.add_node(i_node)
    i_node.set_value(10)
    assert i_node.value == 10

    with pytest.raises(ValueError):
        i_node.set_value("invalid_int")

    # 3. VectorNode
    v_node = VectorNode(graph=graph)
    graph.add_node(v_node)
    v_node.set_components(x=1.0, y=2.0, z=3.0)
    assert v_node.x == 1.0
    assert v_node.y == 2.0
    assert v_node.z == 3.0

    with pytest.raises(ValueError):
        v_node.set_components(x="not_a_number")

    # 4. Property Inspector update for Input Node
    panel = NodeGraphSidePanelWidget(graph=graph)
    panel.update_properties_inspector([f_item])
    assert panel.prop_form_layout.count() > 0


def test_integer_node_click_wait_and_data_entry(qapp):
    """GUI test to change data in an IntegerNode by clicking text area, waiting 2s, entering data, and confirming value."""
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import IntegerNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView

    graph = Graph()
    i_node = IntegerNode(graph=graph)
    i_node.set_value(0)
    graph.add_node(i_node)

    scene = NodeGraphicsScene(graph)
    view = NodeGraphicsView(scene)
    view.show()

    item_i = scene.node_items[i_node]

    proxy_i = None
    for child in item_i.childItems():
        if isinstance(child, QGraphicsProxyWidget):
            proxy_i = child
            break

    assert proxy_i is not None

    spin = proxy_i.widget().findChild(QSpinBox)
    assert spin is not None

    # 1. Click on the text area of the IntegerNode spinbox
    QTest.mouseClick(spin, Qt.LeftButton)
    QApplication.processEvents()

    # 2. Wait 2 seconds
    QTest.qWait(2000)

    # 3. Enter new integer value (42)
    spin.setValue(42)
    QApplication.processEvents()

    # 4. Confirm data has been changed on the underlying node
    assert i_node.value == 42


def test_input_node_data_entry_focus_and_key_handling(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode, StringNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView

    graph = Graph()
    f_node = FloatNode(graph=graph)
    s_node = StringNode(graph=graph)
    graph.add_node(f_node)
    graph.add_node(s_node)

    scene = NodeGraphicsScene(graph)
    view = NodeGraphicsView(scene)
    view.show()

    item_f = scene.node_items[f_node]
    item_s = scene.node_items[s_node]

    # Find embedded spin box and line edit controls
    proxy_f = None
    proxy_s = None

    for child in item_f.childItems():
        if isinstance(child, QGraphicsProxyWidget):
            proxy_f = child
            break

    for child in item_s.childItems():
        if isinstance(child, QGraphicsProxyWidget):
            proxy_s = child
            break

    assert proxy_f is not None
    assert proxy_s is not None

    # Verify focus policies
    assert proxy_f.focusPolicy() == Qt.StrongFocus
    assert proxy_s.focusPolicy() == Qt.StrongFocus

    # Test key event handling when input widget has focus
    spin_widget = proxy_f.widget().findChild(QDoubleSpinBox)
    assert spin_widget is not None
    spin_widget.setFocus()

    # Simulate Backspace key press while spin box is focused
    key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier)
    view.keyPressEvent(key_event)

    # Ensure node was NOT deleted when Backspace was pressed during input focus
    assert f_node in graph.nodes
    assert len(graph.nodes) == 2


def test_input_node_graphics_item_layout_clearance(qapp):
    from freecad_nodegraph.nodes.inputs import FloatNode, VectorNode
    from freecad_nodegraph.gui.items import GraphicsNodeItem

    f_node = FloatNode()

    # Verify z-value on output labels
    for label in GraphicsNodeItem(f_node).label_items:
        assert label.zValue() == 2

    # Verify width leaves clearance
    v_node = VectorNode()
    v_item = GraphicsNodeItem(v_node)
    assert v_item.width >= 210.0


def test_canvas_and_library_help_tooltips(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.items import GraphicsNodeItem
    from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget

    graph = Graph()
    box = BoxNode(graph=graph)
    item = GraphicsNodeItem(box)

    assert item.toolTip() == BoxNode.get_help_summary()

    panel = NodeGraphSidePanelWidget(graph=graph)
    root = panel.node_tree.invisibleRootItem()
    box_tree_item = None
    for i in range(root.childCount()):
        cat = root.child(i)
        for j in range(cat.childCount()):
            child = cat.child(j)
            if child.data(0, 0x0100) == "BoxNode":
                box_tree_item = child
                break

    assert box_tree_item is not None
    assert box_tree_item.toolTip(0) == BoxNode.get_help_summary()


def test_delete_selected_nodes_and_del_key(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)
    graph.connect_sockets(f1.get_output_socket("Value"), box.get_input_socket("Length"))

    scene = NodeGraphicsScene(graph)
    view = NodeGraphicsView(scene)

    assert len(graph.nodes) == 2
    assert len(scene.node_items) == 2
    assert len(scene.edge_items) == 1

    # Select box node item and trigger delete
    item_box = scene.node_items[box]
    item_box.setSelected(True)

    deleted = scene.delete_selected_nodes()
    assert len(deleted) == 1
    assert box not in graph.nodes
    assert len(graph.edges) == 0

    # Select f1 node item and trigger Del key press on view
    item_f1 = scene.node_items[f1]
    item_f1.setSelected(True)

    key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    view.keyPressEvent(key_event)

    assert f1 not in graph.nodes
    assert len(graph.nodes) == 0
    assert len(scene.node_items) == 0


def test_gui_lifecycle_add_connect_move_delete_undo_redo(qapp):
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode

    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)

    # Initial state: 0 nodes, 0 edges
    assert len(editor.graph.nodes) == 0
    assert len(editor.graph.edges) == 0

    # Step 1: Add Node 1 (FloatNode)
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.scene.add_node_item(f1)
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 1

    # Step 2: Add Node 2 (BoxNode)
    box = BoxNode(graph=editor.graph)
    editor.graph.add_node(box)
    editor.scene.add_node_item(box)
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 2

    # Step 3: Connect sockets
    edge = editor.graph.connect_sockets(f1.get_output_socket("Value"), box.get_input_socket("Length"))
    editor.scene.add_edge_item(edge)
    editor.save_to_document_object()
    assert len(editor.graph.edges) == 1

    # Step 4: Move Node 1
    f1.pos_x = 150.0
    f1.pos_y = 200.0
    item_f1 = editor.scene.node_items[f1]
    item_f1.setPos(150.0, 200.0)
    editor.save_to_document_object()
    assert f1.pos_x == 150.0 and f1.pos_y == 200.0

    # Step 5: Delete Node 2 (BoxNode)
    item_box = editor.scene.node_items[box]
    editor.scene.clearSelection()
    item_box.setSelected(True)
    editor.scene.delete_selected_nodes()
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 1
    assert len(editor.graph.edges) == 0

    # --- UNDO ALL STEPS IN REVERSE ---
    # Undo Step 5 (Delete BoxNode)
    assert editor.undo() is True
    assert len(editor.graph.nodes) == 2
    assert len(editor.graph.edges) == 1

    # Undo Step 4 (Move Node 1)
    assert editor.undo() is True
    restored_f1 = [n for n in editor.graph.nodes if n.node_type == "FloatNode"][0]
    assert restored_f1.pos_x == 0.0 and restored_f1.pos_y == 0.0

    # Undo Step 3 (Connect Sockets)
    assert editor.undo() is True
    assert len(editor.graph.edges) == 0

    # Undo Step 2 (Add BoxNode)
    assert editor.undo() is True
    assert len(editor.graph.nodes) == 1

    # Undo Step 1 (Add FloatNode)
    assert editor.undo() is True
    assert len(editor.graph.nodes) == 0

    # --- REDO ALL STEPS FORWARD ---
    # Redo Step 1 (Add FloatNode)
    assert editor.redo() is True
    assert len(editor.graph.nodes) == 1

    # Redo Step 2 (Add BoxNode)
    assert editor.redo() is True
    assert len(editor.graph.nodes) == 2

    # Redo Step 3 (Connect Sockets)
    assert editor.redo() is True
    assert len(editor.graph.edges) == 1

    # Redo Step 4 (Move Node 1)
    assert editor.redo() is True
    redone_f1 = [n for n in editor.graph.nodes if n.node_type == "FloatNode"][0]
    assert redone_f1.pos_x == 150.0 and redone_f1.pos_y == 200.0

    # Redo Step 5 (Delete BoxNode)
    assert editor.redo() is True
    assert len(editor.graph.nodes) == 1
    assert len(editor.graph.edges) == 0


def test_editor_save_guards_during_undo_redo(qapp):
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.nodes.inputs import FloatNode

    class MockUndoDoc:
        def __init__(self):
            self.undo_active = False

        def isUndo(self):
            return self.undo_active

        def openTransaction(self, name):
            raise RuntimeError("Should not open transaction during Undo")

    obj = MockDocumentObject(name="NodeGraph:1")
    doc = MockUndoDoc()
    obj.Document = doc

    editor = NodeGraphEditorWidget(doc_object=obj)

    # When doc.isUndo() is True, save_to_document_object should return immediately without calling openTransaction
    doc.undo_active = True
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.save_to_document_object()

    # Verify _is_syncing prevents reentrancy
    editor._is_syncing = True
    doc.undo_active = False
    editor.save_to_document_object()


def test_editor_handles_deleted_freecad_object(qapp):
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.nodes.inputs import FloatNode

    class DeletedMockObject:
        @property
        def GraphData(self):
            raise ReferenceError("Cannot access attribute 'GraphData' of deleted object")

    deleted_obj = DeletedMockObject()
    editor = NodeGraphEditorWidget(doc_object=deleted_obj)

    # Adding a node triggers save_to_document_object, which encounters ReferenceError on deleted_obj
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.save_to_document_object()

    assert editor.doc_object is None


def test_editor_history_undo_redo(qapp):
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode

    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)

    # Initial state has 0 nodes
    assert len(editor.graph.nodes) == 0

    # Add BoxNode
    box = BoxNode(graph=editor.graph)
    editor.graph.add_node(box)
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 1

    # Add FloatNode
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 2

    # Undo -> 1 node
    assert editor.undo() is True
    assert len(editor.graph.nodes) == 1

    # Redo -> 2 nodes
    assert editor.redo() is True
    assert len(editor.graph.nodes) == 2


def test_copy_cut_paste_duplicate(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)

    scene = NodeGraphicsScene(graph)
    item_box = scene.node_items[box]
    item_box.setSelected(True)

    # Copy
    copied_data = scene.copy_selected_nodes()
    assert len(copied_data["nodes"]) == 1

    # Paste
    pasted = scene.paste_nodes()
    assert len(pasted) == 1
    assert len(graph.nodes) == 3

    # Duplicate
    item_pasted = scene.node_items[pasted[0]]
    item_pasted.setSelected(True)
    dups = scene.duplicate_selected_nodes()
    assert len(dups) == 1
    assert len(graph.nodes) == 4

    # Cut
    item_f1 = scene.node_items[f1]
    scene.clearSelection()
    item_f1.setSelected(True)
    cut_data = scene.cut_selected_nodes()
    assert len(cut_data["nodes"]) == 1
    assert len(graph.nodes) == 3
    assert f1 not in graph.nodes
