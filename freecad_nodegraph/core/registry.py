"""Node registry for registering and instantiating available node types."""

from typing import Dict, List, Type, Optional
from freecad_nodegraph.core.node import BaseNode


class NodeRegistry:
    """Registry maintaining available node classes."""

    _registry: Dict[str, Type[BaseNode]] = {}

    @classmethod
    def register(cls, node_cls: Type[BaseNode]) -> Type[BaseNode]:
        """Register a node class."""
        if not issubclass(node_cls, BaseNode):
            raise TypeError(f"Class {node_cls} must subclass BaseNode")

        node_type = getattr(node_cls, "node_type", node_cls.__name__)
        cls._registry[node_type] = node_cls
        return node_cls

    @classmethod
    def get_node_class(cls, node_type: str) -> Optional[Type[BaseNode]]:
        """Get registered node class by type identifier."""
        return cls._registry.get(node_type)

    @classmethod
    def create_node(cls, node_type: str, **kwargs) -> Optional[BaseNode]:
        """Instantiate a node by node_type."""
        node_cls = cls.get_node_class(node_type)
        if node_cls:
            return node_cls(**kwargs)
        return None

    @classmethod
    def get_all_nodes(cls) -> Dict[str, Type[BaseNode]]:
        """Return dict of all registered node classes."""
        return dict(cls._registry)

    @classmethod
    def get_nodes_by_category(cls) -> Dict[str, List[Type[BaseNode]]]:
        """Return registered nodes grouped by category."""
        categories: Dict[str, List[Type[BaseNode]]] = {}
        for node_cls in cls._registry.values():
            category = getattr(node_cls, "category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(node_cls)
        return categories

    @classmethod
    def clear(cls) -> None:
        """Clear all registered nodes."""
        cls._registry.clear()


def register_node(cls: Type[BaseNode]) -> Type[BaseNode]:
    """Decorator for registering node classes."""
    return NodeRegistry.register(cls)
