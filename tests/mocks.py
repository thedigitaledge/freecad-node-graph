"""Mock objects and test doubles for FreeCAD NodeGraph testing."""

from typing import Dict, Any, Callable

class MockVector:
    """Fallback Vector class when FreeCAD is not available."""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return f"Vector ({self.x}, {self.y}, {self.z})"

    def __eq__(self, other):
        if hasattr(other, "x") and hasattr(other, "y") and hasattr(other, "z"):
            return (self.x, self.y, self.z) == (other.x, other.y, other.z)
        return False


class MockPlacement:
    """Fallback Placement class when FreeCAD is not available."""

    def __init__(self, Base=None, Rotation=None):
        self.Base = Base or MockVector(0, 0, 0)
        self.Rotation = Rotation or (0, 0, 0, 1)

    def __repr__(self):
        return f"Placement [Base: {self.Base}]"


class MockShape:
    """Mock Part shape representation for testing outside FreeCAD."""

    def __init__(self, shape_type: str, params: dict):
        self.shape_type = shape_type
        self.params = params
        self.Placement = params.get("Placement", MockPlacement())

    def __repr__(self):
        return f"<MockShape {self.shape_type} {self.params}>"


class MockDocumentObject:
    """Mock FreeCAD document object for standalone testing outside FreeCAD."""

    def __init__(self, name: str = "NodeGraph:1", label: str = "NodeGraph:1"):
        self.Name = name
        self.Label = label
        self.GraphData = ""
        self.Shape = None
        self.Proxy = None
        self.InList = []
        self.OutList = []
        self.Group = []

        class Document:
            def __init__(self):
                self.Name = "TestDoc"
                self.is_undoing = False
                self.is_redoing = False

            def isUndo(self):
                return self.is_undoing

            def isRedo(self):
                return self.is_redoing

            def openTransaction(self, name):
                pass

            def commitTransaction(self):
                pass

            def abortTransaction(self):
                pass

            def recompute(self):
                pass

        self.Document = Document()

    def addProperty(
        self, prop_type: str, prop_name: str, group: str = "", doc: str = ""
    ):
        if not hasattr(self, prop_name):
            setattr(self, prop_name, "")

    def addObject(self, child_obj):
        if child_obj not in self.Group:
            self.Group.append(child_obj)
            child_obj.InList.append(self)

    def purgeTouched(self):
        pass


class MockFreeCADModule:
    """Mock workbench module when running in standalone Python mode."""

    def __init__(self, name: str, functions: Dict[str, Callable]):
        self.__name__ = name
        for fname, func in functions.items():
            setattr(self, fname, func)


def get_mock_workbenches() -> Dict[str, Any]:
    """Generate fallback mock FreeCAD workbenches and scriptable functions for testing."""
    return {
        "Part": MockFreeCADModule(
            "Part",
            {
                "makeBox": lambda length=10.0, width=10.0, height=10.0: f"<Part.Box {length}x{width}x{height}>",
                "makeCylinder": lambda radius=5.0, height=10.0: f"<Part.Cylinder r={radius} h={height}>",
                "makeSphere": lambda radius=5.0: f"<Part.Sphere r={radius}>",
                "makeCone": lambda radius1=5.0, radius2=0.0, height=10.0: f"<Part.Cone r1={radius1} r2={radius2} h={height}>",
                "makeTorus": lambda radius1=10.0, radius2=2.0: f"<Part.Torus r1={radius1} r2={radius2}>",
                "makeLoft": lambda shapes=None: "<Part.Loft>",
            },
        ),
        "Draft": MockFreeCADModule(
            "Draft",
            {
                "make_line": lambda start=None, end=None: "<Draft.Line>",
                "make_circle": lambda radius=10.0: f"<Draft.Circle r={radius}>",
                "make_rectangle": lambda length=20.0, height=10.0: f"<Draft.Rectangle {length}x{height}>",
                "make_polygon": lambda nfaces=6, radius=10.0: f"<Draft.Polygon n={nfaces} r={radius}>",
            },
        ),
        "Arch": MockFreeCADModule(
            "Arch",
            {
                "makeWall": lambda length=100.0, width=10.0, height=30.0: f"<Arch.Wall {length}x{width}x{height}>",
                "makeStructure": lambda length=10.0, width=10.0, height=100.0: f"<Arch.Structure>",
                "makeWindow": lambda width=5.0, height=10.0: f"<Arch.Window>",
            },
        ),
        "Mesh": MockFreeCADModule(
            "Mesh",
            {
                "createBox": lambda length=10.0, width=10.0, height=10.0: f"<Mesh.Box>",
                "createCylinder": lambda radius=5.0, height=10.0: f"<Mesh.Cylinder>",
            },
        ),
    }
