"""Unit tests for FreeCAD NodeGraph core package."""

import os
import tempfile
import pytest
from freecad_nodegraph.core.socket import Socket, SocketType, DataType
from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.edge import Edge
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry, register_node
from freecad_nodegraph.core.evaluator import GraphEvaluator, EvaluationError
from freecad_nodegraph.core.serializer import GraphSerializer


class AddNode(BaseNode):
    node_type = "TestAddNode"
    category = "Test"
    title = "Add"

    def setup_sockets(self):
        self.add_input("A", DataType.FLOAT, 0.0)
        self.add_input("B", DataType.FLOAT, 0.0)
        self.add_output("Sum", DataType.FLOAT)

    def compute(self):
        a = float(self.get_input_value("A") or 0.0)
        b = float(self.get_input_value("B") or 0.0)
        self.set_output_value("Sum", a + b)


def test_socket_creation():
    node = BaseNode()
    in_sock = node.add_input("In1", DataType.FLOAT, 5.0)
    out_sock = node.add_output("Out1", DataType.FLOAT)

    assert in_sock.is_input
    assert not in_sock.is_output
    assert out_sock.is_output
    assert not in_sock.is_connected
    assert in_sock.default_value == 5.0


def test_graph_and_edge_connection():
    graph = Graph()
    n1 = AddNode(graph=graph)
    n2 = AddNode(graph=graph)
    graph.add_node(n1)
    graph.add_node(n2)

    n1.get_input_socket("A").default_value = 10.0
    n1.get_input_socket("B").default_value = 20.0

    # Connect n1 Sum -> n2 A
    edge = graph.connect_sockets(
        n1.get_output_socket("Sum"),
        n2.get_input_socket("A")
    )

    assert edge is not None
    assert len(graph.edges) == 1
    assert n2.get_input_socket("A").is_connected

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    assert n1.get_output_value("Sum") == 30.0
    assert n2.get_output_value("Sum") == 30.0


def test_invalid_connections():
    graph = Graph()
    n1 = AddNode(graph=graph)
    graph.add_node(n1)

    # Cannot connect socket on same node
    edge = graph.connect_sockets(
        n1.get_output_socket("Sum"),
        n1.get_input_socket("A")
    )
    assert edge is None

    # Cannot connect input to input
    n2 = AddNode(graph=graph)
    graph.add_node(n2)
    edge2 = graph.connect_sockets(
        n1.get_input_socket("A"),
        n2.get_input_socket("A")
    )
    assert edge2 is None


def test_cycle_detection():
    graph = Graph()
    n1 = AddNode(graph=graph)
    n2 = AddNode(graph=graph)
    graph.add_node(n1)
    graph.add_node(n2)

    # n1 -> n2
    graph.connect_sockets(n1.get_output_socket("Sum"), n2.get_input_socket("A"))
    # n2 -> n1 (cycle)
    graph.connect_sockets(n2.get_output_socket("Sum"), n1.get_input_socket("A"))

    evaluator = GraphEvaluator(graph)
    assert evaluator.detect_cycles() is True

    with pytest.raises(EvaluationError):
        evaluator.evaluate()


def test_registry():
    NodeRegistry.register(AddNode)
    assert NodeRegistry.get_node_class("TestAddNode") == AddNode

    node_inst = NodeRegistry.create_node("TestAddNode")
    assert isinstance(node_inst, AddNode)

    categories = NodeRegistry.get_nodes_by_category()
    assert "Test" in categories


def test_serialization():
    NodeRegistry.register(AddNode)

    graph = Graph()
    n1 = AddNode(graph=graph)
    n2 = AddNode(graph=graph)
    graph.add_node(n1)
    graph.add_node(n2)

    n1.get_input_socket("A").default_value = 15.0
    n1.get_input_socket("B").default_value = 25.0
    graph.connect_sockets(n1.get_output_socket("Sum"), n2.get_input_socket("B"))

    data = GraphSerializer.to_dict(graph)
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1

    # Restore in new graph
    new_graph = GraphSerializer.from_dict(data)
    assert len(new_graph.nodes) == 2
    assert len(new_graph.edges) == 1

    evaluator = GraphEvaluator(new_graph)
    evaluator.evaluate()

    # Find nodes in restored graph
    restored_n1 = new_graph.nodes[0]
    assert restored_n1.get_output_value("Sum") == 40.0


def test_graph_history_stack():
    from freecad_nodegraph.core.history import GraphHistory

    history = GraphHistory(max_depth=5)
    assert not history.can_undo()
    assert not history.can_redo()

    history.push_state('{"state": 1}', "State 1")
    history.push_state('{"state": 2}', "State 2")
    history.push_state('{"state": 3}', "State 3")

    assert history.can_undo()
    assert not history.can_redo()
    assert len(history.get_history_records()) == 3

    # Undo to State 2
    rec2 = history.undo()
    assert rec2 is not None
    assert rec2.json_data == '{"state": 2}'
    assert history.can_redo()

    # Redo to State 3
    rec3 = history.redo()
    assert rec3 is not None
    assert rec3.json_data == '{"state": 3}'


def test_file_save_load():
    NodeRegistry.register(AddNode)

    graph = Graph()
    n1 = AddNode(graph=graph)
    n1.get_input_socket("A").default_value = 7.0
    n1.get_input_socket("B").default_value = 8.0
    graph.add_node(n1)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        filepath = tmp.name

    try:
        GraphSerializer.save_to_file(graph, filepath)
        loaded_graph = GraphSerializer.load_from_file(filepath)
        assert len(loaded_graph.nodes) == 1

        evaluator = GraphEvaluator(loaded_graph)
        evaluator.evaluate()
        assert loaded_graph.nodes[0].get_output_value("Sum") == 15.0
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
