"""Unit tests for FreeCAD NodeGraph nodes."""

import pytest
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.nodes.inputs import FloatNode, IntegerNode, StringNode, BooleanNode, VectorNode, PlacementNode
from freecad_nodegraph.nodes.primitives import BoxNode, CylinderNode, SphereNode, ConeNode
from freecad_nodegraph.nodes.booleans import FuseNode, CutNode, CommonNode
from freecad_nodegraph.nodes.transforms import TranslateNode, ExtrudeNode, CompoundNode
from freecad_nodegraph.nodes.output import DocumentOutputNode


def test_node_categories():
    categories = NodeRegistry.get_nodes_by_category()
    assert "Input" in categories
    assert "Output" in categories
    assert "Geometry" in categories

    input_node_types = [cls.node_type for cls in categories["Input"]]
    assert "FloatNode" in input_node_types
    assert "IntegerNode" in input_node_types
    assert "StringNode" in input_node_types
    assert "BooleanNode" in input_node_types
    assert "VectorNode" in input_node_types

    geometry_node_types = [cls.node_type for cls in categories["Geometry"]]
    assert "BoxNode" in geometry_node_types
    assert "CylinderNode" in geometry_node_types
    assert "FuseNode" in geometry_node_types
    assert "TranslateNode" in geometry_node_types

    output_node_types = [cls.node_type for cls in categories["Output"]]
    assert "DocumentOutputNode" in output_node_types


def test_input_nodes_and_error_validation():
    # FloatNode validation
    f_node = FloatNode()
    assert len(f_node.inputs) == 0  # Only output socket
    assert len(f_node.outputs) == 1
    f_node.set_value("42.5")
    assert f_node.value == 42.5
    with pytest.raises(ValueError, match="Invalid float value"):
        f_node.set_value("invalid_float")

    # IntegerNode validation
    i_node = IntegerNode()
    assert len(i_node.inputs) == 0
    i_node.set_value("100")
    assert i_node.value == 100
    with pytest.raises(ValueError, match="Invalid integer value"):
        i_node.set_value("12.34abc")

    # BooleanNode validation
    b_node = BooleanNode()
    assert len(b_node.inputs) == 0
    b_node.set_value("true")
    assert b_node.value is True
    b_node.set_value("off")
    assert b_node.value is False
    with pytest.raises(ValueError, match="Invalid boolean value"):
        b_node.set_value("not_a_bool")

    # VectorNode validation
    v_node = VectorNode()
    assert len(v_node.inputs) == 0
    v_node.set_components(x=10.0, y=20.0, z=30.0)
    assert v_node.x == 10.0 and v_node.y == 20.0 and v_node.z == 30.0
    with pytest.raises(ValueError, match="Invalid float for X component"):
        v_node.set_components(x="bad_x")

    # PlacementNode validation
    p_node = PlacementNode()
    assert len(p_node.inputs) == 0
    p_node.set_position(x=1.0, y=2.0, z=3.0)
    assert p_node.pos_x == 1.0 and p_node.pos_y == 2.0 and p_node.pos_z == 3.0
    with pytest.raises(ValueError, match="Invalid float for Y position"):
        p_node.set_position(y="bad_y")


def test_float_and_vector_nodes():
    graph = Graph()

    vec_node = VectorNode(graph=graph)
    vec_node.set_components(x=10.0, y=20.0, z=30.0)
    graph.add_node(vec_node)

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    vec_val = vec_node.get_output_value("Vector")
    assert vec_val is not None
    assert getattr(vec_val, "x", 0) == 10.0
    assert getattr(vec_val, "y", 0) == 20.0
    assert getattr(vec_val, "z", 0) == 30.0


def test_placement_and_box_nodes():
    graph = Graph()

    place_node = PlacementNode(graph=graph)
    place_node.set_position(x=5.0, y=5.0, z=0.0)
    graph.add_node(place_node)

    box_node = BoxNode(graph=graph)
    box_node.get_input_socket("Length").default_value = 50.0
    box_node.get_input_socket("Width").default_value = 50.0
    box_node.get_input_socket("Height").default_value = 50.0
    graph.add_node(box_node)
    graph.connect_sockets(place_node.get_output_socket("Placement"), box_node.get_input_socket("Placement"))

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    box_shape = box_node.get_output_value("Shape")
    assert box_shape is not None


def test_primitives_and_boolean_fuse():
    graph = Graph()

    box = BoxNode(graph=graph)
    box.get_input_socket("Length").default_value = 10.0
    box.get_input_socket("Width").default_value = 10.0
    box.get_input_socket("Height").default_value = 10.0
    graph.add_node(box)

    cyl = CylinderNode(graph=graph)
    cyl.get_input_socket("Radius").default_value = 5.0
    cyl.get_input_socket("Height").default_value = 15.0
    graph.add_node(cyl)

    fuse = FuseNode(graph=graph)
    graph.add_node(fuse)

    graph.connect_sockets(box.get_output_socket("Shape"), fuse.get_input_socket("Shape A"))
    graph.connect_sockets(cyl.get_output_socket("Shape"), fuse.get_input_socket("Shape B"))

    out = DocumentOutputNode(graph=graph)
    out.get_input_socket("Object Name").default_value = "TestFusedShape"
    graph.add_node(out)

    graph.connect_sockets(fuse.get_output_socket("Shape"), out.get_input_socket("Shape"))

    evaluator = GraphEvaluator(graph)
    evaluated = evaluator.evaluate()

    assert len(evaluated) == 4
    assert fuse.get_output_value("Shape") is not None
    assert out.last_result_shape is not None
    assert out.last_object_name == "TestFusedShape"


def test_transforms_and_other_primitives():
    graph = Graph()

    sphere = SphereNode(graph=graph)
    sphere.get_input_socket("Radius").default_value = 12.0
    graph.add_node(sphere)

    cone = ConeNode(graph=graph)
    cone.get_input_socket("Radius1").default_value = 8.0
    cone.get_input_socket("Radius2").default_value = 2.0
    cone.get_input_socket("Height").default_value = 20.0
    graph.add_node(cone)

    cut = CutNode(graph=graph)
    graph.add_node(cut)

    graph.connect_sockets(sphere.get_output_socket("Shape"), cut.get_input_socket("Base Shape"))
    graph.connect_sockets(cone.get_output_socket("Shape"), cut.get_input_socket("Tool Shape"))

    vec = VectorNode(graph=graph)
    vec.set_components(z=100.0)
    graph.add_node(vec)

    translate = TranslateNode(graph=graph)
    graph.add_node(translate)

    graph.connect_sockets(cut.get_output_socket("Shape"), translate.get_input_socket("Shape"))
    graph.connect_sockets(vec.get_output_socket("Vector"), translate.get_input_socket("Vector"))

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    assert translate.get_output_value("Shape") is not None
