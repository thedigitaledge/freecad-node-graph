"""Unit tests for NodeGraph GUI components in offscreen/qapp context."""

import pytest
from PySide6.QtWidgets import QApplication

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
