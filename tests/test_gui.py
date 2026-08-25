"""Unit tests for NodeGraph GUI components in offscreen/qapp context."""

import pytest
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication
    except ImportError:
        from PyQt5.QtWidgets import QApplication

from freecad_nodegraph.core.socket import DataType

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

    editor = NodeGraphEditorWidget(graph=graph)
    assert editor is not None

    panel = NodeGraphSidePanelWidget(graph=graph)
    assert panel is not None

    task_panel = NodeGraphTaskPanel(graph=graph)
    assert task_panel.widget is not None
    assert len(task_panel.form) == 1


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


def test_add_node_from_library_to_active_editor(qapp):
    from freecad_nodegraph.commands import _active_editors, get_active_editor
    from freecad_nodegraph.document_object import MockDocumentObject
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
    from freecad_nodegraph.nodes.inputs import FloatNode, IntegerNode, StringNode, VectorNode
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
