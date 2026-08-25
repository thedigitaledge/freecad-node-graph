"""Unit tests for AI feature development (AIGraphGenerator, AINode, AIAssistantPanel)."""

import pytest
from PySide6.QtWidgets import QApplication
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.evaluator import GraphEvaluator
from freecad_nodegraph.ai.generator import AIGraphGenerator
from freecad_nodegraph.nodes.ai import AINode, AIPromptNode
from freecad_nodegraph.gui.editor import NodeGraphEditorWindow
from freecad_nodegraph.gui.ai_panel import AIAssistantPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_ai_generator_heuristics():
    generator = AIGraphGenerator()

    # 1. Box and Cylinder Cut
    graph1 = generator.generate_from_prompt("Create a box of 30x30x30 and cut a cylinder of radius 5 height 40 named MyCutModel")
    assert len(graph1.nodes) == 4  # Box, Cylinder, Cut, DocumentOutput
    assert len(graph1.edges) == 3

    out_node = [n for n in graph1.nodes if n.node_type == "DocumentOutputNode"][0]
    assert out_node.get_input_socket("Object Name").default_value == "MyCutModel"

    # Evaluate graph
    evaluator = GraphEvaluator(graph1)
    evaluated = evaluator.evaluate()
    assert len(evaluated) == 4

    # 2. Sphere and Box Fuse
    graph2 = generator.generate_from_prompt("Create a sphere of radius 15 fused with a box of 10x10x10")
    assert len(graph2.nodes) == 4  # Sphere, Box, Fuse, DocumentOutput

    # 3. Translation
    graph3 = generator.generate_from_prompt("Create a box 10x10x10 and translate by 5 10 15")
    assert any(n.node_type == "TranslateNode" for n in graph3.nodes)
    assert any(n.node_type == "VectorNode" for n in graph3.nodes)


def test_ai_generator_llm_handler():
    generator = AIGraphGenerator()

    def mock_llm_handler(prompt: str):
        return {
            "nodes": [
                {"id": "n1", "type": "BoxNode", "pos_x": 0, "pos_y": 0, "inputs": {"Length": 50, "Width": 50, "Height": 50}},
                {"id": "n2", "type": "DocumentOutputNode", "pos_x": 300, "pos_y": 0, "inputs": {"Object Name": "LLMBox"}},
            ],
            "edges": [
                {"from_node": "n1", "from_socket": "Shape", "to_node": "n2", "to_socket": "Shape"},
            ],
        }

    generator.set_llm_handler(mock_llm_handler)
    graph = generator.generate_from_prompt("Build a custom cube using LLM")
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    box_node = [n for n in graph.nodes if n.node_type == "BoxNode"][0]
    assert box_node.get_input_socket("Length").default_value == 50


def test_ai_nodes():
    # AINode
    ai_node = AINode()
    ai_node.get_input_socket("Prompt").default_value = "Create a box 15x15x15"
    ai_node.compute()

    summary = ai_node.get_output_value("Summary")
    shape = ai_node.get_output_value("Shape")
    assert "Generated graph" in summary
    assert shape is not None

    # AIPromptNode
    p_node = AIPromptNode()
    p_node.get_input_socket("System Prompt").default_value = "SysPromptTest"
    p_node.get_input_socket("User Prompt").default_value = "UserPromptTest"
    p_node.compute()

    formatted = p_node.get_output_value("Formatted Prompt")
    assert "[System: SysPromptTest]" in formatted
    assert "[User: UserPromptTest]" in formatted


def test_ai_assistant_gui_panel(qapp):
    graph = Graph()
    editor = NodeGraphEditorWindow(graph=graph)

    panel = editor.ai_panel
    assert panel is not None

    # Preset selection
    panel.preset_combo.setCurrentIndex(1)
    assert len(panel.prompt_text.toPlainText()) > 0

    # Generate graph via GUI action
    panel.generate_graph()
    assert len(editor.graph.nodes) > 0
    assert "Successfully generated graph" in panel.log_view.toPlainText()

    # Clear prompt
    panel.clear_prompt()
    assert panel.prompt_text.toPlainText() == ""
    assert panel.log_view.toPlainText() == ""

    # Test toolbar toggle
    editor.toggle_ai_panel()
    assert editor.right_tabs.currentWidget() == panel
