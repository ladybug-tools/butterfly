"""A collection of useful methods."""
try:
    import Rhino as rc
    import scriptcontext as sc
    from Grasshopper.Kernel.Types import GH_ObjectWrapper as goo
except ImportError:
    pass

from butterfly.utilities import loadOFPointsFile, loadOFFacesFile
import os

tolerance = sc.doc.ModelAbsoluteTolerance


def ghWrapper(objs):
    """Put item in a Grasshopper Object Wrapper."""
    try:
        return (goo(obj) for obj in objs)
    except Exception as e:
        raise Exception(
            'Failed to wrap butterfly object in Grasshopper wrapper:\n\t{}'.format(e))


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
    mesh = rc.Geometry.Mesh()

    for p in pts:
        mesh.Vertices.Add(rc.Geometry.Point3d(*p))

    for face in faces:
        if len(face) < 5:
            mesh.Faces.AddFace(*face)
        elif len(face) == 5:
            mesh.Faces.AddFace(*face[:3])
            mesh.Faces.AddFace(face[0], face[2], face[3], face[4])
        elif len(face) == 8:
            mesh.Faces.AddFace(*face[:4])
            mesh.Faces.AddFace(face[0], face[3], face[4], face[7])
            mesh.Faces.AddFace(face[7], face[4], face[5], face[6])
        else:
            try:
                mesh.Faces.AddFace(*face[:4])
                mesh.Faces.AddFace(*face[:1] + (face[4:]))
            except:
                msg = "One of the faces has %d vertices." % len(face)
                print msg

    # scale mesh to Rhion units if not meters
    if convertToMeters != 1:
        mesh.Scale(1.0 / convertToMeters)

    return mesh


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
    return tuple(rc.Geometry.Point3d(*p) for p in pts)
