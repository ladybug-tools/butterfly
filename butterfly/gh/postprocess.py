# coding=utf-8
"""Grasshopper post process functions."""
import os
try:
    import Rhino as rc
except ImportError:
    pass

import gzip


def loadOFMeshToRhino(polyMeshFolder, convertToMeters=1):
    """Convert OpenFOAM mesh to a Rhino Mesh."""
    def splitLine(l, t=float):
        return tuple(t(s) for s in l.split('(')[-1].replace(')', '').split())

    if not polyMeshFolder:
        return

    pf = os.path.join(polyMeshFolder, 'points')
    ff = os.path.join(polyMeshFolder, 'faces')

    pfgz = os.path.join(polyMeshFolder, 'points.gz')
    ffgz = os.path.join(polyMeshFolder, 'faces.gz')

    if not os.path.isfile(pf) or not os.path.isfile(ff):
        # check for zipped files
        if not os.path.isfile(pfgz) or not os.path.isfile(ffgz):
            raise Exception("Can't find point or faces file.")
        else:
            ptFile = gzip.open(pfgz, 'rb')
            faceFile = gzip.open(ffgz, 'rb')
    else:
        ptFile = open(pf, 'rb')
        faceFile = open(ff, 'rb')

    try:
        # read points
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
    except Exception as e:
        raise Exception('Failed to load points file:\n{}'.format(e))
    finally:
        ptFile.close()

    # read faces
    try:
        for l in xrange(18):
            faceFile.readline()

        nFaces = int(faceFile.readline())
        faceFile.readline()
        faces = tuple(
            (splitLine(faceFile.readline(), t=int))
            for pt in xrange(nFaces)
        )
    except Exception as e:
        raise Exception('Failed to load faces file:\n{}'.format(e))
    finally:
        faceFile.close()

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

    # scale mesh to Rhion units if not meters
    if convertToMeters != 1:
        mesh.Scale(1.0 / convertToMeters)

    return mesh


def loadOFPointsToRhino(polyMeshFolder, convertToMeters=1):
    """Load OpenFOAM points as Rhino points."""
    def splitLine(l, t=float):
        return tuple(t(s) for s in l.split('(')[-1].replace(')', '').split())

    pf = os.path.join(polyMeshFolder, 'points')
    pfgz = os.path.join(polyMeshFolder, 'points.gz')

    if not os.path.isfile(pf):
        # check for zipped files
        if not os.path.isfile(pfgz):
            print "Can't find points file."
            return
        else:
            ptFile = gzip.open(pfgz, 'rb')
    else:
        ptFile = open(pf, 'rb')

    # read points
    try:
        for l in xrange(17):
            ptFile.readline()

        try:
            # blockMesh
            line = ptFile.readline()
            nPoints = int(line[0])
            pts = (
                rc.Geometry.Point3d(*pt)
                for pt in eval(line[1:].replace(" ", ", "))
            )
        except:
            # snappyHexMesh
            line = ptFile.readline()
            nPoints = int(line)
            ptFile.readline()
            pts = (
                rc.Geometry.Point3d(*splitLine(ptFile.readline()))
                for pt in xrange(nPoints)
            )
    except Exception as e:
        raise Exception('Failed to load points file:\n{}'.format(e))
    else:
        if convertToMeters != 1:
            pts = tuple(pt / convertToMeters for pt in pts)
        else:
            pts = tuple(pts)
    finally:
        ptFile.close()

    return pts
