"""PyTest-BDD step definitions for Node Graph UI automation behavior tests."""

import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from freecad_nodegraph.commands import _active_editors
from freecad_nodegraph.gui.editor import NodeGraphEditorWidget
from freecad_nodegraph.gui.panel import NodeGraphSidePanelWidget
from freecad_nodegraph.nodes.inputs import FloatNode
from freecad_nodegraph.nodes.primitives import BoxNode
from tests.mocks import MockDocumentObject

# Load scenarios from feature file
FEATURE_FILE = os.path.join(os.path.dirname(__file__), "../features/node_graph_ui.feature")
scenarios(FEATURE_FILE)


@pytest.fixture
@given("a fresh Node Graph document and editor workspace", target_fixture="fresh_workspace")
def fresh_workspace():
    _active_editors.clear()
    obj = MockDocumentObject(name="NodeGraph:1")
    editor = NodeGraphEditorWidget(doc_object=obj)
    editor.show()
    _active_editors[obj] = (editor, editor)
    panel = NodeGraphSidePanelWidget(graph=editor.graph)
    return {"obj": obj, "editor": editor, "panel": panel}


@given('I add a "FloatNode" and a "BoxNode" to the graph')
def add_float_and_box(fresh_workspace):
    editor = fresh_workspace["editor"]
    f1 = FloatNode(graph=editor.graph)
    box = BoxNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.graph.add_node(box)
    editor.scene.add_node_item(f1)
    editor.scene.add_node_item(box)
    editor.save_to_document_object()
    fresh_workspace["f1"] = f1
    fresh_workspace["box"] = box


@given('I add a "FloatNode" to the graph')
def add_float_node(fresh_workspace):
    editor = fresh_workspace["editor"]
    f1 = FloatNode(graph=editor.graph)
    editor.graph.add_node(f1)
    editor.scene.add_node_item(f1)
    editor.save_to_document_object()
    fresh_workspace["f1"] = f1


@given(parsers.parse('I connect the "{out_sock}" output of "FloatNode" to the "{in_sock}" input of "BoxNode"'))
@when(parsers.parse('I connect the "{out_sock}" output of "FloatNode" to the "{in_sock}" input of "BoxNode"'))
def connect_sockets(fresh_workspace, out_sock, in_sock):
    editor = fresh_workspace["editor"]
    f1 = fresh_workspace["f1"]
    box = fresh_workspace["box"]
    out_s = f1.get_output_socket(out_sock)
    in_s = box.get_input_socket(in_sock)
    edge = editor.graph.connect_sockets(out_s, in_s)
    editor.scene.add_edge_item(edge)
    editor.save_to_document_object()


@when(parsers.parse('I double click on the "{node_type}" item in the Node Library task panel'))
def double_click_node_library_item(fresh_workspace, node_type):
    panel = fresh_workspace["panel"]
    root = panel.node_tree.invisibleRootItem()
    target_item = None
    for i in range(root.childCount()):
        cat = root.child(i)
        for j in range(cat.childCount()):
            child = cat.child(j)
            if child.data(0, 0x0100) == node_type:
                target_item = child
                break
    assert target_item is not None
    panel.on_node_library_double_clicked(target_item)


@when(parsers.parse('I set the float node value to "{val_str}"'))
def set_float_val(fresh_workspace, val_str):
    editor = fresh_workspace["editor"]
    f1 = fresh_workspace["f1"]
    f1.set_value(float(val_str))
    editor.save_to_document_object()


@when(parsers.parse('I select and delete the "{node_title}" on the canvas'))
def delete_node_on_canvas(fresh_workspace, node_title):
    editor = fresh_workspace["editor"]
    box = fresh_workspace["box"]
    item_box = editor.scene.node_items[box]
    editor.scene.clearSelection()
    item_box.setSelected(True)
    editor.scene.delete_selected_nodes()
    editor.save_to_document_object()


@when(parsers.parse('I add a "{node_type}" to the graph'))
def add_single_node(fresh_workspace, node_type):
    editor = fresh_workspace["editor"]
    if node_type == "BoxNode":
        node = BoxNode(graph=editor.graph)
    else:
        node = FloatNode(graph=editor.graph)
    editor.graph.add_node(node)
    editor.scene.add_node_item(node)
    editor.save_to_document_object()


@when("I trigger UI undo")
def trigger_undo(fresh_workspace):
    editor = fresh_workspace["editor"]
    assert editor.undo() is True


@when("I trigger UI redo")
def trigger_redo(fresh_workspace):
    editor = fresh_workspace["editor"]
    assert editor.redo() is True


@then(parsers.parse('the active editor graph should contain {count:d} node of type "{node_type}"'))
def check_node_count_and_type(fresh_workspace, count, node_type):
    editor = fresh_workspace["editor"]
    matching = [n for n in editor.graph.nodes if n.node_type == node_type]
    assert len(matching) == count


@then(parsers.parse("{count:d} node item should be displayed on the graphics scene"))
@then(parsers.parse("{count:d} node items should be displayed on the graphics scene"))
def check_scene_node_items(fresh_workspace, count):
    editor = fresh_workspace["editor"]
    assert len(editor.scene.node_items) == count


@then(parsers.parse("the graph should contain {count:d} connected edge between the nodes"))
def check_graph_edges(fresh_workspace, count):
    editor = fresh_workspace["editor"]
    assert len(editor.graph.edges) == count


@then(parsers.parse("{count:d} edge item should be visible on the graphics scene"))
def check_scene_edge_items(fresh_workspace, count):
    editor = fresh_workspace["editor"]
    assert len(editor.scene.edge_items) == count


@then(parsers.parse('the "FloatNode" value should equal {expected:f}'))
def check_float_val(fresh_workspace, expected):
    f1 = fresh_workspace["f1"]
    assert f1.value == expected


@then(parsers.parse('the output value of "FloatNode" should compute to {expected:f}'))
def check_float_output(fresh_workspace, expected):
    f1 = fresh_workspace["f1"]
    f1.compute()
    assert f1.get_output_value("Value") == expected


@then(parsers.parse("the graph should contain {count:d} node"))
@then(parsers.parse("the graph should contain {count:d} nodes"))
def check_total_graph_nodes(fresh_workspace, count):
    editor = fresh_workspace["editor"]
    assert len(editor.graph.nodes) == count


@then(parsers.parse("the graph should contain {count:d} edges"))
def check_total_graph_edges(fresh_workspace, count):
    editor = fresh_workspace["editor"]
    assert len(editor.graph.edges) == count
