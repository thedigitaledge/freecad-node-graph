"""AI Nodes for FreeCAD NodeGraph Workbench."""

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import register_node
from freecad_nodegraph.ai.generator import AIGraphGenerator
from freecad_nodegraph.core.evaluator import GraphEvaluator


@register_node
class AINode(BaseNode):
    """Node that generates CAD shapes dynamically from natural language AI prompts."""

    node_type = "AINode"
    category = "AI"
    title = "AI Geometry Generator"

    def setup_sockets(self) -> None:
        self.add_input("Prompt", DataType.STRING, default_value="Create a box of size 20x20x20")
        self.add_output("Shape", DataType.SHAPE)
        self.add_output("Summary", DataType.STRING)

    def compute(self) -> None:
        prompt = self.get_input_value("Prompt") or "Create a box of size 10x10x10"
        generator = AIGraphGenerator()
        sub_graph = generator.generate_from_prompt(str(prompt), clear_existing=True)

        evaluator = GraphEvaluator(sub_graph)
        try:
            evaluated = evaluator.evaluate(force=True)
            res_shape = None
            for node in sub_graph.nodes:
                out_shape = node.get_output_value("Shape")
                if out_shape is not None:
                    res_shape = out_shape

            self.set_output_value("Shape", res_shape)
            self.set_output_value("Summary", f"Generated graph with {len(sub_graph.nodes)} nodes from prompt: '{prompt}'")
        except Exception as e:
            self.set_output_value("Shape", None)
            self.set_output_value("Summary", f"Error generating geometry: {str(e)}")


@register_node
class AIPromptNode(BaseNode):
    """Node for formatting and processing AI system and user prompt instructions."""

    node_type = "AIPromptNode"
    category = "AI"
    title = "AI Prompt Assistant"

    def setup_sockets(self) -> None:
        self.add_input("System Prompt", DataType.STRING, default_value="You are a CAD Assistant.")
        self.add_input("User Prompt", DataType.STRING, default_value="Create a cylinder of radius 10 and height 30")
        self.add_output("Formatted Prompt", DataType.STRING)

    def compute(self) -> None:
        sys_p = self.get_input_value("System Prompt") or ""
        user_p = self.get_input_value("User Prompt") or ""
        formatted = f"[System: {sys_p}]\n[User: {user_p}]"
        self.set_output_value("Formatted Prompt", formatted)
