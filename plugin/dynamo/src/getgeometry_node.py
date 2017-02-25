# assign inputs
_BFObjects, colors_ = IN
geometries = None

try:
    from butterfly_dynamo.geometry import BFMeshToMesh
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))
else:
    from itertools import chain

def getGeometry(obj):
    """Get Dynamo geometry from butterfly objects."""
    try:
        return obj.geometry
    except AttributeError:
        try:
            return obj.geometries
        except AttributeError:
            print '{} has no geometry!'.format(type(obj))

if _BFObjects:
    geo = chain.from_iterable(getGeometry(obj) for obj in _BFObjects)
    
    try:
        geo = tuple(geo)
    except TypeError:
        pass
    else:
        if not colors_:
            col = [None] * len(geo)
        else:
            l = len(colors_)
            col = (colors_[c % l] for c, g in enumerate(geo))

        geometries = (BFMeshToMesh(g, c) for g, c in zip(geo, col))


# assign outputs to OUT
OUT = (geometries,)