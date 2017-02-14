# assign inputs
_name, _BFGeometries, refRegions_, make2dParams_, _meshParams_, expandBlockMesh_, _run = IN
blockPts = case = None

try:
    from butterfly_dynamo.case import Case
    from butterfly_dynamo.geometry import xyzToPoint
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/dynamo/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


if _run and _name and _BFGeometries: 
    # create OpenFoam Case
    case = Case.fromBFGeometries(_name, tuple(_BFGeometries),
        meshingParameters=_meshParams_, make2dParameters=make2dParams_)
    
    for reg in refRegions_:
        case.addRefinementRegion(reg)
    
    if expandBlockMesh_:
        case.blockMeshDict.expandUniformByCellsCount(1)
    
    blockPts = (xyzToPoint(v) for v in case.blockMeshDict.vertices)
    
    case.save(overwrite=(_run + 1) % 2)


# assign outputs to OUT
OUT = blockPts, case