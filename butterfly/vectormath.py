"""Calculate anitclockwise angle between two vectors."""
import math

__all__ = ('angleAnitclockwise', 'crossProduct')


def length(v):
    """calculate length of vector."""
    if len(v) == 2:
        v = (v[0], v[1], 0)

    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def dotProduct(v, w):
    """calcualte dot product."""
    return v[0] * w[0] + v[1] * w[1]


def determinant(v, w):
    """determinant."""
    return v[0] * w[1] - v[1] * w[0]


def innerAngle(v, w):
    """calculate inner angle between two vectors.

    modified from: http://stackoverflow.com/a/31735880
    """
    cosx = dotProduct(v, w) / (length(v) * length(w))
    rad = math.acos(cosx)  # in radians
    return rad * 180 / math.pi  # returns degrees


def angleAnitclockwise(v1, v2):
    """Calculate clockwise angle between two 2D vectors."""
    v1 = v1[:2]
    v2 = v2[:2]

    inner = innerAngle(v1, v2)
    det = determinant(v1, v2)

    if inner % 360 == 0:
        return 0

    if det > 0:
        # if the det > 0 then A is immediately clockwise of B
        return inner
    else:
        # this is a property of the det. If the det < 0 then B is clockwise of A
        return 360 - inner

def crossProduct(v1, v2, norm=True):
    """Calculate cross product of two 3d vector."""
    v = (v1[1] * v2[2] - v1[2] * v2[1], -v1[0] * v2[2] + v1[2] * v2[0],
         v1[0] * v2[1] - v1[1] * v2[0])

    if norm:
        return normalize(v)
    else:
        return v

def normalize(v):
    """Normalize a vector."""
    l = length(v)
    return tuple(c / l for c in v)

def move(p, v):
    """move a point along a vector and return a new pt."""
    return tuple(i + j for i, j in zip(p, v))

def scale(v, s):
    """Scale b by s."""
    return tuple(i * s for i in v)

def sums(vectors):
    """Add up a number of vectors."""
    return tuple(sum(v) for v in zip(*vectors))

def rotate(origin, point, angle):
    u"""
    Rotate a point anitclockwise by a given angle around a given origin.
    The angle should be given in degrees.

    modified from: http://stackoverflow.com/a/34374437/4394669
    """
    angle = math.radians(angle)
    ox, oy, oz = origin
    px, py, pz = point
    cosine = math.cos(angle)
    sine = math.sin(angle)
    qx = ox + cosine * (px - ox) - sine * (py - oy)
    qy = oy + sine * (px - ox) + cosine * (py - oy)
    return qx, qy, pz
