"""A collection of useful methods."""
try:
    import clr
    import System
    clr.AddReference('ProtoGeometry')
    import Autodesk.DesignScript.Geometry as DSGeometry
    _loc = tuple(a.Location
                 for a in System.AppDomain.CurrentDomain.GetAssemblies()
                 if 'MeshToolkit' in a.FullName)
    assert len(_loc) != 0, \
        'Failed to find MeshToolkit!\n' \
        'You need to install MeshToolkit from package maneger to use Butterfly.'

    clr.AddReferenceToFileAndPath(_loc)
    import Autodesk.Dynamo.MeshToolkit as MeshToolkit
except ImportError:
    pass

import os
from butterfly.utilities import loadOFPointsFile, loadOFFacesFile

__all__ = ('loadOFMesh', 'loadOFPoints', tolerace)

tolerance = 0.001


def loadOFMesh(polyMeshFolder, convertToMeters=1):
    """Convert OpenFOAM mesh to a Rhino Mesh."""
    if not polyMeshFolder:
        return

    pff = tuple(f for f in os.listdir(polyMeshFolder) if f.startswith('points'))
    fff = tuple(f for f in os.listdir(polyMeshFolder) if f.startswith('faces'))

    if pff:
        pf = os.path.join(polyMeshFolder, pff[0])
    else:
        raise ValueError('Failed to find points file at {}'.format(polyMeshFolder))
    if fff:
        ff = os.path.join(polyMeshFolder, fff[0])
    else:
        raise ValueError('Failed to find faces file at {}'.format(polyMeshFolder))

    pts = loadOFPointsFile(pf)
    faces = loadOFFacesFile(ff)

    # create the mesh
    dsPts = (DSGeometry.Point.ByCoordinates(*p) for p in pts)
    ind = (i for face in faces for t in _triangulate(face) for i in t)
    mesh = MeshToolkit.Mesh.ByVerticesAndIndices(dsPts, ind)
    # scale mesh to Rhion units if not meters
    if convertToMeters != 1:
        mesh.Scale(1.0 / convertToMeters)

    return mesh


def _triangulate(v):
    """return indices as tuples with of 3 vertices."""
    return ((v[0], v[i], v[i + 1]) for i in range(1, len(v) - 1))


# TODO: Scale points based on convertToMeters
def loadOFPoints(polyMeshFolder, convertToMeters=1):
    """Load OpenFOAM points as Rhino points."""
    if not polyMeshFolder:
        return

    pff = tuple(f for f in os.listdir(polyMeshFolder) if f.startswith('points'))

    if pff:
        pf = os.path.join(polyMeshFolder, pff[0])
    else:
        raise ValueError('Failed to find points file at {}'.format(polyMeshFolder))

    pts = loadOFPointsFile(pf)
    return tuple(DSGeometry.Point.ByCoordinates(*p) for p in pts)
