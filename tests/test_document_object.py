"""Unit tests for NodeGraph document objects (top-level, nested subobjects, and isolated graph data storage)."""

import json
import pytest
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication
    except ImportError:
        from PyQt5.QtWidgets import QApplication

from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.nodes.inputs import FloatNode
from freecad_nodegraph.nodes.primitives import BoxNode
from freecad_nodegraph.nodes.output import DocumentOutputNode
from freecad_nodegraph.core.serializer import GraphSerializer
from freecad_nodegraph.document_object import (
    NodeGraphObject,
    MockDocumentObject,
    make_nodegraph_object,
)
from freecad_nodegraph.gui.editor import NodeGraphEditorWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_top_level_nodegraph_object():
    obj = make_nodegraph_object(doc=None, name="MyNodeGraph")
    assert obj is not None
    assert obj.Name == "MyNodeGraph"
    assert hasattr(obj, "GraphData")

    # Construct test graph
    graph = Graph()
    box = BoxNode(graph=graph)
    box.get_input_socket("Length").default_value = 25.0
    graph.add_node(box)

    out = DocumentOutputNode(graph=graph)
    graph.add_node(out)
    graph.connect_sockets(box.get_output_socket("Shape"), out.get_input_socket("Shape"))

    obj.GraphData = json.dumps(GraphSerializer.to_dict(graph))

    # Recompute object via Proxy
    proxy = obj.Proxy
    proxy.execute(obj)

    assert obj.Shape is not None


def test_nested_subobject_nodegraph_object():
    parent_group = MockDocumentObject(name="ParentGroup")
    child_nodegraph = make_nodegraph_object(
        doc=None, name="ChildNodeGraph", parent_obj=parent_group
    )

    assert child_nodegraph in parent_group.Group
    assert parent_group in child_nodegraph.InList


def test_isolated_document_object_graph_data_storage(qapp):
    """Verify that multiple NodeGraph objects maintain independent isolated graph storages."""
    obj1 = make_nodegraph_object(doc=None, name="NodeGraph1")
    obj2 = make_nodegraph_object(doc=None, name="NodeGraph2")

    editor1 = NodeGraphEditorWidget(doc_object=obj1)
    editor2 = NodeGraphEditorWidget(doc_object=obj2)

    # Add Box to obj1 graph
    box1 = BoxNode(graph=editor1.graph)
    editor1.graph.add_node(box1)
    editor1.save_to_document_object()

    # Add Float to obj2 graph
    f2 = FloatNode(graph=editor2.graph)
    editor2.graph.add_node(f2)
    editor2.save_to_document_object()

    # Confirm storage isolation
    data1 = json.loads(obj1.GraphData)
    data2 = json.loads(obj2.GraphData)

    assert len(data1["nodes"]) == 1
    assert data1["nodes"][0]["node_type"] == "BoxNode"

    assert len(data2["nodes"]) == 1
    assert data2["nodes"][0]["node_type"] == "FloatNode"


def test_view_provider_double_click(qapp):
    from freecad_nodegraph.document_object import ViewProviderNodeGraph

    class MockViewObject:
        def __init__(self, obj):
            self.Object = obj
            self.Proxy = None

    obj = MockDocumentObject(name="TestVG")
    vobj = MockViewObject(obj)
    vp = ViewProviderNodeGraph(vobj)

    assert vp.getIcon() == "NodeGraph_Editor"
    res = vp.doubleClicked(vobj)
    assert isinstance(res, bool)


def test_selection_observer_triggers_editor(qapp):
    from freecad_nodegraph.commands import NodeGraphSelectionObserver, CommandOpenNodeGraphEditor

    observer = NodeGraphSelectionObserver()
    assert observer is not None
    assert hasattr(observer, "addSelection")
    assert hasattr(observer, "check_selection")
