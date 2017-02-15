"""A collection of useful methods."""
try:
    import clr
    clr.AddReference('ProtoGeometry')
    import Autodesk.DesignScript.Geometry as DSGeometry
except ImportError:
    pass

import os
from butterfly.utilities import loadOFPointsFile, loadOFFacesFile

__all__ = ('loadOFMesh', 'loadOFPoints')

tolerance = 0.001


def loadOFMesh(polyMeshFolder, convertToMeters=1, innerMesh=True):
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
    faces = loadOFFacesFile(ff, innerMesh)

    # create the mesh
    pts = tuple(DSGeometry.Point.ByCoordinates(*p) for p in pts)
    mesh = tuple(
        DSGeometry.PolyCurve.ByPoints((pts[i] for i in f), True)
        for f in faces)

    # scale mesh to Dynamo units if not meters
    if convertToMeters != 1:
        mesh = tuple(m.Scale(1.0 / convertToMeters) for m in mesh)

    # dispose points
    for pt in pts:
        pt.Dispose()
    return mesh


def _triangulate(v):
    """return indices as tuples with of 3 vertices."""
    return ((v[0], v[i], v[i + 1]) for i in range(1, len(v) - 1))


# TODO(): Scale points based on convertToMeters
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
