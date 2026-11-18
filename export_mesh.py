"""Manufacturing STL with an absolute millimeter deflection tolerance."""
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer


def export_stl_mm(shape, path, tolerance=.005, angular_tolerance=.05):
    # build123d.export_stl uses relative deflection, over-refining tiny blends.
    mesh = BRepMesh_IncrementalMesh(shape.wrapped, tolerance, False,
                                   angular_tolerance, True)
    mesh.Perform()
    writer = StlAPI_Writer()
    writer.ASCIIMode = False
    if not writer.Write(shape.wrapped, str(path)):
        raise ValueError(f'STL export failed: {path}')
