"""Node definitions for FreeCAD NodeGraph."""

from freecad_nodegraph.nodes.inputs import (
    FloatNode,
    IntegerNode,
    StringNode,
    BooleanNode,
    VectorNode,
    PlacementNode,
)
from freecad_nodegraph.nodes.primitives import (
    BoxNode,
    CylinderNode,
    SphereNode,
    ConeNode,
)
from freecad_nodegraph.nodes.booleans import FuseNode, CutNode, CommonNode
from freecad_nodegraph.nodes.transforms import (
    TranslateNode,
    ExtrudeNode,
    CompoundNode,
)
from freecad_nodegraph.nodes.output import DocumentOutputNode
from freecad_nodegraph.nodes.ai import AINode, AIPromptNode

__all__ = [
    "FloatNode",
    "IntegerNode",
    "StringNode",
    "BooleanNode",
    "VectorNode",
    "PlacementNode",
    "BoxNode",
    "CylinderNode",
    "SphereNode",
    "ConeNode",
    "FuseNode",
    "CutNode",
    "CommonNode",
    "TranslateNode",
    "ExtrudeNode",
    "CompoundNode",
    "DocumentOutputNode",
    "AINode",
    "AIPromptNode",
]
