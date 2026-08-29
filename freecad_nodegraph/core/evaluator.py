"""Graph evaluation engine for topological sorting and node execution."""

from typing import List, Set, Tuple
from freecad_nodegraph.core.graph import Graph
from freecad_nodegraph.core.node import BaseNode


class EvaluationError(Exception):
    """Exception raised when graph evaluation fails or cycle is detected."""

    pass


class GraphEvaluator:
    """Evaluates node graphs using topological sorting."""

    def __init__(self, graph: Graph):
        self.graph = graph

    def detect_cycles(self) -> bool:
        """Returns True if the graph contains a cycle."""
        visited: Set[BaseNode] = set()
        rec_stack: Set[BaseNode] = set()

        def dfs(node: BaseNode) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for downstream in node.get_downstream_nodes():
                if downstream not in visited:
                    if dfs(downstream):
                        return True
                elif downstream in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in self.graph.nodes:
            if node not in visited:
                if dfs(node):
                    return True

        return False

    def get_topological_order(self) -> List[BaseNode]:
        """Returns nodes ordered such that dependencies precede dependent nodes."""
        if self.detect_cycles():
            raise EvaluationError("Graph contains a cyclic dependency.")

        in_degree = {node: 0 for node in self.graph.nodes}
        for node in self.graph.nodes:
            for downstream in node.get_downstream_nodes():
                in_degree[downstream] += 1

        queue = [node for node in self.graph.nodes if in_degree[node] == 0]
        topo_order: List[BaseNode] = []

        while queue:
            node = queue.pop(0)
            topo_order.append(node)

            for downstream in node.get_downstream_nodes():
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        if len(topo_order) != len(self.graph.nodes):
            raise EvaluationError("Failed to sort all nodes; possible cyclic dependency.")

        return topo_order

    def evaluate(self, force: bool = False) -> List[BaseNode]:
        """Evaluates nodes in topological order."""
        nodes_to_eval = self.get_topological_order()
        evaluated_nodes = []

        for node in nodes_to_eval:
            if force or node.is_dirty:
                node.compute()
                node.mark_clean()
                evaluated_nodes.append(node)

        return evaluated_nodes
