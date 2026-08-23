Available Nodes
===============

Inputs
------
- **Float Value**: Provides a single floating-point number.
- **Vector**: Constructs a 3D vector (X, Y, Z).
- **Placement**: Constructs a placement transformation from a position vector.

Primitives
----------
- **Box**: Generates a 3D rectangular box with Length, Width, Height.
- **Cylinder**: Generates a 3D cylinder with Radius and Height.
- **Sphere**: Generates a 3D sphere with Radius.
- **Cone**: Generates a 3D cone with Radius1, Radius2, and Height.

Booleans
--------
- **Fuse (Union)**: Combines two 3D shapes.
- **Cut (Difference)**: Subtracts Tool Shape from Base Shape.
- **Common (Intersection)**: Computes intersection of two shapes.

Transforms & Features
---------------------
- **Translate**: Translates a shape by a vector offset.
- **Extrude**: Extrudes a shape along a vector direction.
- **Compound**: Combines multiple shapes into a compound Part shape.

Output
------
- **Document Output**: Injects final computed 3D shape into FreeCAD active document.
