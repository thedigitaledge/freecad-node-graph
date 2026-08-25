"""FreeCAD NodeGraph Workbench package."""

from freecad_nodegraph import nodes
from freecad_nodegraph.document_object import (
    NodeGraphObject,
    create_nodegraph_object,
    NodeGraphSelectionObserver,
)

__version__ = "0.1.0"
__all__ = [
    "nodes",
    "NodeGraphObject",
    "create_nodegraph_object",
    "NodeGraphSelectionObserver",
]
