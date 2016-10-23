"""Calculate anitclockwise angle between two vectors."""
from math import acos, sqrt, pi

__all__ = ('angleAnitclockwise', 'crossProduct')


def length(v):
    """calculate length of vector."""
    if len(v) == 2:
        v = (v[0], v[1], 0)

    return sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


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
    rad = acos(cosx)  # in radians
    return rad * 180 / pi  # returns degrees


def angleAnitclockwise(v1, v2):
    """Calculate clockwise angle between two 2D vectors."""
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

def crossProduct(v1, v2, normalize=True):
    """Calculate cross product of two 3d vector."""
    v = (v1[1] * v2[2] - v1[2] * v2[1], -v1[0] * v2[2] + v1[2] * v2[0],
         v1[0] * v2[1] - v1[1] * v2[0])

    if normalize:
        l = length(v)
        return tuple(c / l for c in v)
    else:
        return v
