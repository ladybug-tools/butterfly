"""Grasshopper post process functions."""
import os
try:
    import Rhino as rc
except ImportError:
    pass


def loadOFMeshToRhino(polyMeshFolder):
    """Convert OpenFOAM mesh to a Rhino Mesh."""
    def splitLine(l, t=float):
        return tuple(t(s) for s in l.split('(')[-1].replace(')', '').split())

    if not polyMeshFolder:
        return

    pf = os.path.join(polyMeshFolder, 'points')
    ff = os.path.join(polyMeshFolder, 'faces')

    if not os.path.isfile(pf) or not os.path.isfile(ff):
        print "Can't find point and faces file."
        return

    # read points
    with open(pf, 'rb') as ptFile:
        for l in xrange(17):
            ptFile.readline()

        try:
            # blockMesh
            line = ptFile.readline()
            nPoints = int(line[0])
            pts = tuple(
                rc.Geometry.Point3d(*pt)
                for pt in eval(line[1:].replace(" ", ", "))
            )
        except:
            # snappyHexMesh
            line = ptFile.readline()
            nPoints = int(line)
            ptFile.readline()
            pts = tuple(
                rc.Geometry.Point3d(*splitLine(ptFile.readline()))
                for pt in xrange(nPoints)
            )

    # read faces
    with open(ff, 'rb') as faceFile:
        for l in xrange(18):
            faceFile.readline()

        nFaces = int(faceFile.readline())
        faceFile.readline()
        faces = tuple(
            (splitLine(faceFile.readline(), t=int))
            for pt in xrange(nFaces)
        )

    # create the mesh
    mesh = rc.Geometry.Mesh()

    for p in pts:
        mesh.Vertices.Add(p)

    for face in faces:
        if len(face) < 5:
            mesh.Faces.AddFace(*face)
        elif len(face) == 5:
            mesh.Faces.AddFace(*face[:3])
            mesh.Faces.AddFace(*face[:1] + (face[3:]))
        elif len(face) == 8:
            mesh.Faces.AddFace(*face[:4])
            mesh.Faces.AddFace(*(face[0], face[3], face[4], face[7]))
            mesh.Faces.AddFace(*(face[7], face[4], face[5], face[6]))
        else:
            try:
                mesh.Faces.AddFace(*face[:4])
                mesh.Faces.AddFace(*face[:1] + (face[4:]))
            except:
                msg = "One of the faces has %d vertices." % len(face)
                print msg

    return mesh


def loadOFPointsToRhino(polyMeshFolder):
    """Load OpenFOAM points as Rhino points."""
    def splitLine(l, t=float):
        return tuple(t(s) for s in l.split('(')[-1].replace(')', '').split())

    pf = os.path.join(polyMeshFolder, 'points')

    if not os.path.isfile(pf):
        print "Can't find point and faces file."
        return

    # read points
    with open(pf, 'rb') as ptFile:
        for l in xrange(17):
            ptFile.readline()

        try:
            # blockMesh
            line = ptFile.readline()
            nPoints = int(line[0])
            pts = tuple(
                rc.Geometry.Point3d(*pt)
                for pt in eval(line[1:].replace(" ", ", "))
            )
        except:
            # snappyHexMesh
            line = ptFile.readline()
            nPoints = int(line)
            ptFile.readline()
            pts = tuple(
                rc.Geometry.Point3d(*splitLine(ptFile.readline()))
                for pt in xrange(nPoints)
            )

    return pts


def loadOFVectorsToRhino(resultsFolder, variable='U'):
    """Load OpenFOAM vector results such as velocity."""
    def splitLine(l, t=float):
        return tuple(t(s) for s in l.split('(')[-1].replace(')', '').split())

    pf = os.path.join(resultsFolder, variable)

    if not os.path.isfile(pf):
        print "Can't find vector file."
        return

    # read vectors
    with open(pf, 'rb') as ptFile:
        for l in xrange(21):
            line = ptFile.readline()
        nVectors = int(line)
        ptFile.readline()
        vectors = tuple(
            rc.Geometry.Vector3d(*splitLine(ptFile.readline()))
            for pt in xrange(nVectors)
        )
    return vectors
