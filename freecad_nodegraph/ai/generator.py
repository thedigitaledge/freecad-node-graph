"""AI Graph Generator for converting natural language prompts into parametric node graphs."""

import re
from typing import Dict, Any, Optional, List, Callable
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.registry import NodeRegistry
from freecad_nodegraph.nodes.primitives import BoxNode, CylinderNode, SphereNode, ConeNode
from freecad_nodegraph.nodes.booleans import FuseNode, CutNode, CommonNode
from freecad_nodegraph.nodes.transforms import TranslateNode
from freecad_nodegraph.nodes.inputs import VectorNode
from freecad_nodegraph.nodes.output import DocumentOutputNode


class AIGraphGenerator:
    """Generates CAD node graphs from text prompts using heuristic parsing or LLM handlers."""

    def __init__(self):
        self._llm_handler: Optional[Callable[[str], Dict[str, Any]]] = None

    def set_llm_handler(self, handler: Optional[Callable[[str], Dict[str, Any]]]) -> None:
        """Set a custom LLM provider handler function for prompt parsing."""
        self._llm_handler = handler

    def generate_from_prompt(
        self, prompt: str, graph: Optional[Graph] = None, clear_existing: bool = True
    ) -> Graph:
        """Generates a node graph from a natural language prompt."""
        if graph is None:
            graph = Graph()
        elif clear_existing:
            graph.clear()

        if self._llm_handler:
            try:
                spec = self._llm_handler(prompt)
                if spec and isinstance(spec, dict):
                    self._build_graph_from_spec(graph, spec)
                    return graph
            except Exception:
                pass  # Fallback to rule-based parser on LLM failure

        self._parse_and_build_heuristic(prompt, graph)
        return graph

    def _parse_and_build_heuristic(self, prompt: str, graph: Graph) -> None:
        """Rule-based heuristic parser for natural language CAD prompts."""
        text = prompt.lower()

        # Extract numeric values helper
        def extract_numbers(s: str) -> List[float]:
            return [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", s)]

        dims = extract_numbers(text)

        pos_x = 50.0
        pos_y = 100.0

        # Boolean operations check
        has_cut = any(w in text for w in ["cut", "subtract", "difference", "remove", "hole"])
        has_fuse = any(w in text for w in ["fuse", "union", "combine", "join", "add"])
        has_common = any(w in text for w in ["common", "intersection", "intersect"])
        has_translate = any(w in text for w in ["translate", "move", "offset", "shift"])

        shape_nodes = []

        if "box" in text or "cube" in text or "block" in text:
            box = BoxNode(graph=graph)
            box.pos_x = pos_x
            box.pos_y = pos_y
            pos_x += 220.0

            l = dims[0] if len(dims) > 0 else 10.0
            w = dims[1] if len(dims) > 1 else l
            h = dims[2] if len(dims) > 2 else l

            box.get_input_socket("Length").default_value = l
            box.get_input_socket("Width").default_value = w
            box.get_input_socket("Height").default_value = h

            graph.add_node(box)
            shape_nodes.append(box)

        if "cylinder" in text or "pipe" in text or "tube" in text or "hole" in text:
            cyl = CylinderNode(graph=graph)
            cyl.pos_x = pos_x
            cyl.pos_y = pos_y + (120 if shape_nodes else 0)
            pos_x += 220.0

            rad = 5.0
            height = 20.0
            rad_match = re.search(r"radius\s*=?\s*(\d+(?:\.\d+)?)", text)
            if rad_match:
                rad = float(rad_match.group(1))
            elif len(dims) > 0 and not ("box" in text or "cube" in text):
                rad = dims[0]

            height_match = re.search(r"height\s*=?\s*(\d+(?:\.\d+)?)", text)
            if height_match:
                height = float(height_match.group(1))
            elif len(dims) > 1 and not ("box" in text or "cube" in text):
                height = dims[1]

            cyl.get_input_socket("Radius").default_value = rad
            cyl.get_input_socket("Height").default_value = height

            graph.add_node(cyl)
            shape_nodes.append(cyl)

        if "sphere" in text or "ball" in text:
            sph = SphereNode(graph=graph)
            sph.pos_x = pos_x
            sph.pos_y = pos_y + (120 if shape_nodes else 0)
            pos_x += 220.0

            rad = 10.0
            rad_match = re.search(r"radius\s*=?\s*(\d+(?:\.\d+)?)", text)
            if rad_match:
                rad = float(rad_match.group(1))
            elif dims and not ("box" in text or "cylinder" in text):
                rad = dims[0]

            sph.get_input_socket("Radius").default_value = rad

            graph.add_node(sph)
            shape_nodes.append(sph)

        if "cone" in text:
            cone = ConeNode(graph=graph)
            cone.pos_x = pos_x
            cone.pos_y = pos_y + (120 if shape_nodes else 0)
            pos_x += 220.0

            cone.get_input_socket("Radius1").default_value = dims[0] if len(dims) > 0 else 10.0
            cone.get_input_socket("Radius2").default_value = dims[1] if len(dims) > 1 else 2.0
            cone.get_input_socket("Height").default_value = dims[2] if len(dims) > 2 else 20.0

            graph.add_node(cone)
            shape_nodes.append(cone)

        # Default primitive if no primitive mentioned explicitly
        if not shape_nodes:
            box = BoxNode(graph=graph)
            box.pos_x = pos_x
            box.pos_y = pos_y
            pos_x += 220.0
            graph.add_node(box)
            shape_nodes.append(box)

        last_shape_node = shape_nodes[0]

        # Connect boolean operations if multiple shapes created or explicitly requested
        if len(shape_nodes) >= 2:
            base_node = shape_nodes[0]
            tool_node = shape_nodes[1]

            if has_cut:
                bool_node = CutNode(graph=graph)
                bool_node.pos_x = pos_x
                bool_node.pos_y = pos_y + 40
                pos_x += 220.0
                graph.add_node(bool_node)

                graph.connect_sockets(base_node.get_output_socket("Shape"), bool_node.get_input_socket("Base Shape"))
                graph.connect_sockets(tool_node.get_output_socket("Shape"), bool_node.get_input_socket("Tool Shape"))
                last_shape_node = bool_node

            elif has_common:
                bool_node = CommonNode(graph=graph)
                bool_node.pos_x = pos_x
                bool_node.pos_y = pos_y + 40
                pos_x += 220.0
                graph.add_node(bool_node)

                graph.connect_sockets(base_node.get_output_socket("Shape"), bool_node.get_input_socket("Shape A"))
                graph.connect_sockets(tool_node.get_output_socket("Shape"), bool_node.get_input_socket("Shape B"))
                last_shape_node = bool_node

            else:  # default or fuse
                bool_node = FuseNode(graph=graph)
                bool_node.pos_x = pos_x
                bool_node.pos_y = pos_y + 40
                pos_x += 220.0
                graph.add_node(bool_node)

                graph.connect_sockets(base_node.get_output_socket("Shape"), bool_node.get_input_socket("Shape A"))
                graph.connect_sockets(tool_node.get_output_socket("Shape"), bool_node.get_input_socket("Shape B"))
                last_shape_node = bool_node

        # Check for translation
        if has_translate:
            vec_node = VectorNode(graph=graph)
            vec_node.pos_x = pos_x - 100
            vec_node.pos_y = pos_y + 180
            graph.add_node(vec_node)

            trans_nums = extract_numbers(re.sub(r"box|cube|cylinder|sphere|cone|radius|height|length|width", "", text))
            if trans_nums:
                vec_node.set_components(
                    x=trans_nums[0] if len(trans_nums) > 0 else 0.0,
                    y=trans_nums[1] if len(trans_nums) > 1 else 0.0,
                    z=trans_nums[2] if len(trans_nums) > 2 else 0.0,
                )

            trans_node = TranslateNode(graph=graph)
            trans_node.pos_x = pos_x
            trans_node.pos_y = pos_y
            pos_x += 220.0
            graph.add_node(trans_node)

            graph.connect_sockets(last_shape_node.get_output_socket("Shape"), trans_node.get_input_socket("Shape"))
            graph.connect_sockets(vec_node.get_output_socket("Vector"), trans_node.get_input_socket("Vector"))
            last_shape_node = trans_node

        # Add Document Output node
        out_node = DocumentOutputNode(graph=graph)
        out_node.pos_x = pos_x
        out_node.pos_y = pos_y
        graph.add_node(out_node)

        name_match = re.search(r"name[d]?\s+([a-zA-Z0-9_]+)", prompt, re.IGNORECASE)
        if name_match:
            out_node.get_input_socket("Object Name").default_value = name_match.group(1)

        graph.connect_sockets(last_shape_node.get_output_socket("Shape"), out_node.get_input_socket("Shape"))

    def _build_graph_from_spec(self, graph: Graph, spec: Dict[str, Any]) -> None:
        """Build graph from a structured specification dictionary (LLM format)."""
        nodes_spec = spec.get("nodes", [])
        edges_spec = spec.get("edges", [])

        node_map = {}
        for n_data in nodes_spec:
            ntype = n_data.get("type")
            node = NodeRegistry.create_node(ntype, graph=graph)
            if node:
                node.pos_x = n_data.get("pos_x", 0.0)
                node.pos_y = n_data.get("pos_y", 0.0)
                for k, v in n_data.get("inputs", {}).items():
                    sock = node.get_input_socket(k)
                    if sock:
                        sock.default_value = v
                graph.add_node(node)
                node_map[n_data.get("id", node.id)] = node

        for e_data in edges_spec:
            from_node = node_map.get(e_data.get("from_node"))
            to_node = node_map.get(e_data.get("to_node"))
            if from_node and to_node:
                out_sock = from_node.get_output_socket(e_data.get("from_socket"))
                in_sock = to_node.get_input_socket(e_data.get("to_socket"))
                if out_sock and in_sock:
                    graph.connect_sockets(out_sock, in_sock)
