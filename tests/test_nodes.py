"""Unit tests for FreeCAD NodeGraph nodes."""

import pytest
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator
from freecad_nodegraph.nodes.inputs import FloatNode, VectorNode, PlacementNode
from freecad_nodegraph.nodes.primitives import BoxNode, CylinderNode, SphereNode, ConeNode
from freecad_nodegraph.nodes.booleans import FuseNode, CutNode, CommonNode
from freecad_nodegraph.nodes.transforms import TranslateNode, ExtrudeNode, CompoundNode
from freecad_nodegraph.nodes.output import DocumentOutputNode


def test_float_and_vector_nodes():
    graph = Graph()

    fx = FloatNode(graph=graph)
    fx.get_input_socket("Value").default_value = 10.0
    graph.add_node(fx)

    fy = FloatNode(graph=graph)
    fy.get_input_socket("Value").default_value = 20.0
    graph.add_node(fy)

    fz = FloatNode(graph=graph)
    fz.get_input_socket("Value").default_value = 30.0
    graph.add_node(fz)

    vec_node = VectorNode(graph=graph)
    graph.add_node(vec_node)

    graph.connect_sockets(fx.get_output_socket("Value"), vec_node.get_input_socket("X"))
    graph.connect_sockets(fy.get_output_socket("Value"), vec_node.get_input_socket("Y"))
    graph.connect_sockets(fz.get_output_socket("Value"), vec_node.get_input_socket("Z"))

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    vec_val = vec_node.get_output_value("Vector")
    assert vec_val is not None
    assert getattr(vec_val, "x", 0) == 10.0
    assert getattr(vec_val, "y", 0) == 20.0
    assert getattr(vec_val, "z", 0) == 30.0


def test_placement_and_box_nodes():
    graph = Graph()

    vec_node = VectorNode(graph=graph)
    vec_node.get_input_socket("X").default_value = 5.0
    vec_node.get_input_socket("Y").default_value = 5.0
    vec_node.get_input_socket("Z").default_value = 0.0
    graph.add_node(vec_node)

    place_node = PlacementNode(graph=graph)
    graph.add_node(place_node)
    graph.connect_sockets(vec_node.get_output_socket("Vector"), place_node.get_input_socket("Position"))

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
    vec.get_input_socket("Z").default_value = 100.0
    graph.add_node(vec)

    translate = TranslateNode(graph=graph)
    graph.add_node(translate)

    graph.connect_sockets(cut.get_output_socket("Shape"), translate.get_input_socket("Shape"))
    graph.connect_sockets(vec.get_output_socket("Vector"), translate.get_input_socket("Vector"))

    evaluator = GraphEvaluator(graph)
    evaluator.evaluate()

    assert translate.get_output_value("Shape") is not None
