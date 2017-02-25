# assign inputs
_name, _BFGeometries, refRegions_, _windVector, _refWindHeight_, _landscape_, make2dParams_, _meshParams_, _tunnelParams_, _run = IN
pts = case = None

try:
    from butterfly_dynamo.windtunnel import WindTunnelDS
    from butterfly_dynamo.geometry import xyzToPoint
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


def main():
    wt = WindTunnelDS.fromGeometriesWindVectorAndParameters(
        _name, _BFGeometries, _windVector, _tunnelParams_, _landscape_,
        _meshParams_, _refWindHeight_)
        
    for region in refRegions_:
        wt.addRefinementRegion(region)
    
    # save with overwrite set to False. User can clean the folder using purge if they need to.
    case = wt.save(overwrite=(_run + 1) % 2, make2dParameters=make2dParams_)
    
    print "Wind tunnel dimensions: {}, {} and {}".format(
        case.blockMeshDict.width, case.blockMeshDict.length, case.blockMeshDict.height)
    
    print "Number of divisions: {}, {} and {}".format(*wt.blockMeshDict.nDivXYZ)
    
    pts = (xyzToPoint(v) for v in case.blockMeshDict.vertices)

    return wt, pts, case

if _run and _name and _BFGeometries and _windVector:
        tunnel, pts, case = main()


# assign outputs to OUT
OUT = pts, case