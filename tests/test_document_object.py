"""Unit tests for NodeGraph document objects (top-level, nested subobjects, naming, and isolated graph data storage)."""

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
    get_next_nodegraph_name,
)
from freecad_nodegraph.gui.editor import NodeGraphEditorWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_nodegraph_object_naming():
    name1 = get_next_nodegraph_name(doc=None)
    assert name1 == "NodeGraph:1"

    obj1 = make_nodegraph_object(doc=None)
    assert obj1.Name == "NodeGraph:1" or obj1.Label == "NodeGraph:1"


def test_top_level_nodegraph_object():
    obj = make_nodegraph_object(doc=None)
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
        doc=None, parent_obj=parent_group
    )

    assert child_nodegraph in parent_group.Group
    assert parent_group in child_nodegraph.InList


def test_isolated_document_object_graph_data_storage(qapp):
    """Verify that multiple NodeGraph objects maintain independent isolated graph storages."""
    obj1 = make_nodegraph_object(doc=None)
    obj2 = make_nodegraph_object(doc=None)

    editor1 = NodeGraphEditorWidget(doc_object=obj1)
    editor2 = NodeGraphEditorWidget(doc_object=obj2)

    assert editor1.windowTitle() == obj1.Name
    assert editor2.windowTitle() == obj2.Name

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

    obj = MockDocumentObject(name="NodeGraph:1")
    vobj = MockViewObject(obj)
    vp = ViewProviderNodeGraph(vobj)

    assert vp.getIcon() == "NodeGraph_Editor"
    res = vp.doubleClicked(vobj)
    assert isinstance(res, bool)


def test_editor_save_and_sync_undo_redo(qapp):
    class MockDoc:
        def __init__(self):
            self.transactions = []

        def openTransaction(self, name):
            self.transactions.append(("open", name))

        def commitTransaction(self):
            self.transactions.append(("commit", None))

    obj = MockDocumentObject(name="NodeGraph:1")
    doc = MockDoc()
    obj.Document = doc

    editor = NodeGraphEditorWidget(doc_object=obj)

    box = BoxNode(graph=editor.graph)
    editor.graph.add_node(box)
    editor.save_to_document_object()

    assert len(doc.transactions) == 2
    assert doc.transactions[0] == ("open", "Modify Node Graph")
    assert doc.transactions[1] == ("commit", None)

    initial_json = obj.GraphData

    # Modify graph and save
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.save_to_document_object()

    assert len(editor.graph.nodes) == 2

    # Simulate Undo restoring initial_json
    obj.GraphData = initial_json
    editor.sync_from_document_object()

    assert len(editor.graph.nodes) == 1
    assert len(editor.scene.node_items) == 1


def test_selection_observer_triggers_editor(qapp):
    from freecad_nodegraph.commands import NodeGraphSelectionObserver

    observer = NodeGraphSelectionObserver()
    assert observer is not None
    assert hasattr(observer, "addSelection")
    assert hasattr(observer, "check_selection")


def test_command_open_editor_shows_task_panel(qapp, monkeypatch):
    import freecad_nodegraph.commands as commands
    from freecad_nodegraph.gui.panel import NodeGraphTaskPanel

    shown_dialogs = []

    class MockControl:
        @staticmethod
        def showDialog(panel):
            shown_dialogs.append(panel)

    class MockFreeCADGui:
        Control = MockControl

    monkeypatch.setattr(commands, "FreeCADGui", MockFreeCADGui)

    cmd = commands.CommandOpenNodeGraphEditor()
    obj = MockDocumentObject(name="NodeGraph:1")
    cmd.Activated(doc_object=obj)

    assert len(shown_dialogs) == 1
    assert isinstance(shown_dialogs[0], NodeGraphTaskPanel)


def test_selection_observer_closes_task_panel(qapp, monkeypatch):
    import freecad_nodegraph.commands as commands

    closed_dialogs = []

    class MockControl:
        @staticmethod
        def closeDialog():
            closed_dialogs.append(True)

    class MockFreeCADGui:
        Control = MockControl

    monkeypatch.setattr(commands, "FreeCADGui", MockFreeCADGui)

    observer = commands.NodeGraphSelectionObserver()
    observer.clearSelection("Doc")
    assert len(closed_dialogs) == 1

    observer.close_task_panel()
    assert len(closed_dialogs) == 2


def test_show_task_panel_safely_handles_existing_dialog(qapp, monkeypatch):
    import freecad_nodegraph.commands as commands
    from freecad_nodegraph.gui.panel import NodeGraphTaskPanel

    closed_dialogs = []
    shown_dialogs = []

    class MockControl:
        @staticmethod
        def activeDialog():
            return "ActiveDialog"

        @staticmethod
        def closeDialog():
            closed_dialogs.append(True)

        @staticmethod
        def showDialog(panel):
            shown_dialogs.append(panel)

    class MockFreeCADGui:
        Control = MockControl

    monkeypatch.setattr(commands, "FreeCADGui", MockFreeCADGui)

    commands.show_task_panel_safely(None)

    assert len(closed_dialogs) == 1
    assert len(shown_dialogs) == 1
    assert isinstance(shown_dialogs[0], NodeGraphTaskPanel)


def test_nodegraph_object_onchanged_and_document_observer_callbacks(qapp):
    from freecad_nodegraph.commands import _active_editors, NodeGraphDocumentObserver
    from freecad_nodegraph.document_object import NodeGraphObject, MockDocumentObject
    from freecad_nodegraph.gui.editor import NodeGraphEditorWidget

    _active_editors.clear()

    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)
    editor.show()
    _active_editors[obj] = (editor, editor)

    proxy = NodeGraphObject(obj)

    # Adding a node to editor and saving
    box = BoxNode(graph=editor.graph)
    editor.graph.add_node(box)
    editor.save_to_document_object()
    assert len(editor.graph.nodes) == 1

    initial_data = json.dumps(GraphSerializer.to_dict(Graph()))

    # Modify GraphData directly on obj (simulating C++ document undo)
    obj.GraphData = initial_data

    # Test Proxy onChanged
    proxy.onChanged(obj, "GraphData")
    assert len(editor.graph.nodes) == 0

    # Test NodeGraphDocumentObserver callbacks
    doc_observer = NodeGraphDocumentObserver()
    doc_observer.slotUndo(None)
    doc_observer.slotRedo(None)
    doc_observer.slotChangedObject(obj, "GraphData")
    doc_observer.slotChangeProperty(obj, "GraphData")

    _active_editors.clear()


def test_subwindow_activated_deactivates_task_panel(qapp, monkeypatch):
    import freecad_nodegraph.commands as commands

    closed_dialogs = []

    class MockControl:
        @staticmethod
        def closeDialog():
            closed_dialogs.append(True)

    class MockFreeCADGui:
        Control = MockControl

    monkeypatch.setattr(commands, "FreeCADGui", MockFreeCADGui)

    # When active subwindow becomes None (e.g. clicking off to a non-subwindow area)
    commands.on_subwindow_activated(None)
    assert len(closed_dialogs) == 1

    # When active subwindow belongs to a non-NodeGraph widget
    class MockSubWindow:
        def widget(self):
            return None

    commands.on_subwindow_activated(MockSubWindow())
    assert len(closed_dialogs) == 2
