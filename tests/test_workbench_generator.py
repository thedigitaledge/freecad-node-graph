"""Unit tests for FreeCAD workbench discovery and dynamic scriptable node generation."""

import pytest
from PySide6.QtWidgets import QApplication
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.workbench_generator import (
    discover_workbench_functions,
    generate_node_class_for_function,
)
from freecad_nodegraph.gui.editor import NodeGraphEditorWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_workbench_discovery():
    discovered = discover_workbench_functions()
    assert isinstance(discovered, dict)
    assert "Part" in discovered
    assert "Draft" in discovered
    assert "Arch" in discovered

    part_funcs = discovered["Part"]
    assert "makeBox" in part_funcs
    assert "makeCylinder" in part_funcs


def test_generated_node_creation_and_execution():
    def custom_make_box(length=10.0, width=20.0, height=30.0):
        return f"BoxResult_{length}_{width}_{height}"

    node_cls = generate_node_class_for_function("TestWB", "makeBox", custom_make_box)
    assert node_cls.category == "TestWB"

    graph = Graph()
    node = node_cls(graph=graph)
    graph.add_node(node)

    # Check sockets
    sock_names = [s.name for s in node.inputs]
    assert "length" in sock_names
    assert "width" in sock_names
    assert "height" in sock_names

    # Compute
    node.compute()
    res = node.get_output_value("Result")
    assert res == "BoxResult_10.0_20.0_30.0"

    # Change socket default value
    node.get_input_socket("length").default_value = 50.0
    node.mark_dirty()
    assert node.get_output_value("Result") == "BoxResult_50.0_20.0_30.0"


def test_workbench_editor_toolbars(qapp):
    graph = Graph()
    window = NodeGraphEditorWindow(graph=graph)
    assert window is not None

    # Check toolbars created on editor window
    toolbars = window.findChildren(type(window.findChild(type(window.findChildren(type(window)))) or window.toolBarArea))
    # Confirm window contains toolbars for Part, Draft, Arch, etc.
    tb_names = [tb.windowTitle() for tb in window.children() if hasattr(tb, "windowTitle") and "Workbench" in tb.windowTitle()]
    assert any("Part Workbench" in name for name in tb_names)
