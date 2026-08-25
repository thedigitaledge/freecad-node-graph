"""Unit tests for NodeGraph GUI components in offscreen/qapp context."""

import pytest
from PySide6.QtWidgets import QApplication, QTreeWidget, QGroupBox, QDoubleSpinBox
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
    from freecad_nodegraph.gui.editor import NodeGraphEditorWindow, NodeGraphTaskPanel

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)

    scene = NodeGraphicsScene(graph)
    assert len(scene.node_items) == 2

    view = NodeGraphicsView(scene)
    assert view is not None

    window = NodeGraphEditorWindow(graph=graph, title="NodeGraph")
    assert window is not None
    assert window.windowTitle() == "NodeGraph"
    assert window.centralWidget() == window.view

    task_panel = NodeGraphTaskPanel(editor_window=window)
    assert task_panel.form == task_panel
    assert task_panel.getStandardButtons() == 0
    assert window.task_panel == task_panel


def test_task_panel_search_and_properties(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.editor import NodeGraphEditorWindow, NodeGraphTaskPanel

    graph = Graph()
    box = BoxNode(graph=graph)
    graph.add_node(box)

    window = NodeGraphEditorWindow(graph=graph)
    task_panel = NodeGraphTaskPanel(editor_window=window)
    window.set_task_panel(task_panel)

    # 1. Test search filter in node tree
    task_panel.search_edit.setText("Box")
    root = task_panel.node_tree.invisibleRootItem()
    # Find matching items
    box_found = False
    for i in range(root.childCount()):
        cat_item = root.child(i)
        for j in range(cat_item.childCount()):
            child = cat_item.child(j)
            if "Box" in child.text(0) and not child.isHidden():
                box_found = True
    assert box_found

    # Test filtering out
    task_panel.search_edit.setText("NonExistentNodeNameXYZ")
    visible_count = 0
    for i in range(root.childCount()):
        cat_item = root.child(i)
        for j in range(cat_item.childCount()):
            child = cat_item.child(j)
            if not child.isHidden():
                visible_count += 1
    assert visible_count == 0

    # Reset search
    task_panel.search_edit.setText("")

    # 2. Test spawning node by double clicking
    initial_node_count = len(graph.nodes)
    for i in range(root.childCount()):
        cat_item = root.child(i)
        if cat_item.childCount() > 0:
            item_to_click = cat_item.child(0)
            task_panel.on_node_library_double_clicked(item_to_click, 0)
            break
    assert len(graph.nodes) == initial_node_count + 1

    # 3. Test selection changed updating Properties Inspector
    scene_box_item = window.scene.node_items[box]
    scene_box_item.setSelected(True)
    assert task_panel.prop_group.title() == "Node: Box"
    # Form layout should have row items for Box inputs (Length, Width, Height)
    assert task_panel.prop_form_layout.rowCount() > 0


def test_command_open_editor(qapp):
    from freecad_nodegraph.commands import CommandOpenNodeGraphEditor
    cmd = CommandOpenNodeGraphEditor()
    res = cmd.GetResources()
    assert "Pixmap" in res
    assert cmd.IsActive() is True

    # Activate command
    cmd.Activated()
    from freecad_nodegraph.commands import _editor_window, _task_panel
    assert _editor_window is not None
    assert _task_panel is not None
    assert _editor_window.task_panel == _task_panel


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
