"""Unit tests for NodeGraph GUI components in offscreen/qapp context."""

import pytest
from PySide6.QtWidgets import QApplication
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
    from freecad_nodegraph.nodes.inputs import FloatNode, VectorNode
    from freecad_nodegraph.nodes.primitives import BoxNode
    from freecad_nodegraph.gui.scene import NodeGraphicsScene
    from freecad_nodegraph.gui.view import NodeGraphicsView
    from freecad_nodegraph.gui.editor import NodeGraphEditorWindow

    graph = Graph()
    f1 = FloatNode(graph=graph)
    box = BoxNode(graph=graph)
    graph.add_node(f1)
    graph.add_node(box)

    scene = NodeGraphicsScene(graph)
    assert len(scene.node_items) == 2

    view = NodeGraphicsView(scene)
    assert view is not None

    window = NodeGraphEditorWindow(graph=graph)
    assert window is not None
    assert window.windowTitle() == "FreeCAD NodeGraph Editor"


def test_socket_colors_and_labels(qapp):
    from freecad_nodegraph.core.graph import Graph
    from freecad_nodegraph.nodes.inputs import FloatNode, VectorNode
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
