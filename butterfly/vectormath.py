"""Calculate anitclockwise angle between two vectors."""
import math

__all__ = ('angle_anitclockwise', 'cross_product', 'project')


def length(v):
    """calculate length of vector."""
    if len(v) == 2:
        v = (v[0], v[1], 0)

    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def dot_product(v, w):
    """calcualte dot product."""
    if len(v) == 2:
        v = (v[0], v[1], 0)
    if len(w) == 2:
        w = (w[0], w[1], 0)

    return v[0] * w[0] + v[1] * w[1] + v[2] * w[2]


def determinant(v, w):
    """determinant."""
    return v[0] * w[1] - v[1] * w[0]


def inner_angle(v, w):
    """calculate inner angle between two vectors.

    modified from: http://stackoverflow.com/a/31735880
    """
    cosx = dot_product(v, w) / (length(v) * length(w))
    rad = math.acos(cosx)  # in radians
    return rad * 180 / math.pi  # returns degrees


def angle_anitclockwise(v1, v2):
    """Calculate clockwise angle between two 2D vectors."""
    v1 = v1[:2]
    v2 = v2[:2]

    inner = inner_angle(v1, v2)
    det = determinant(v1, v2)

    if inner % 360 == 0:
        return 0

    if det > 0:
        # if the det > 0 then A is immediately clockwise of B
        return inner
    else:
        # this is a property of the det. If the det < 0 then B is clockwise of A
        return 360 - inner


def cross_product(v1, v2, norm=True):
    """Calculate cross product of two 3d vector."""
    # handle 2D vectors
    v1 = (v1[0], v1[1], 0) if len(v1) == 2 else v1
    v2 = (v2[0], v2[1], 0) if len(v2) == 2 else v2

    v = (v1[1] * v2[2] - v1[2] * v2[1], -v1[0] * v2[2] + v1[2] * v2[0],
         v1[0] * v2[1] - v1[1] * v2[0])

    if norm:
        return normalize(v)
    else:
        return v


def normalize(v):
    """Normalize a vector."""
    ln = length(v)
    if ln == 0:
        raise ValueError('A vector with length of 0 cannot be normalized.')
    return tuple(c / ln for c in v)


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
    u"""Rotate a point anitclockwise by a given angle around a given origin.

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


def subtract(v1, v2):
    """subtract v2 from v1."""
    return tuple(a - b for a, b in zip(v1, v2))


def project(p, o, n):
    """Project a point3d on a plane.

    Args:
        p: Point.
        o: Origin of plane.
        n: Plane normal.
    Returns:
        projected point as (x, y, z)
    """
    n = normalize(n)
    dif = scale(n, dot_product(subtract(p, o), n))
    return subtract(p, dif)
