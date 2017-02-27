# assign inputs
_name, _BFGeometries, refRegions_, make2dParams_, _meshParams_, expandBlockMesh_, _run = IN
blockPts = case = None

try:
    from butterfly_dynamo.case import Case
    from butterfly_dynamo.geometry import xyzToPoint
    import butterfly_dynamo.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
        '\nYou can download butterfly from Package Manager.' + \
        '\nOpen an issue on github if you think this is a bug:' + \
        ' https://github.com/ladybug-analysis-tools/butterfly/issues'

    raise ImportError('{}\n{}'.format(msg, e))


if _run and _name and _BFGeometries:
    # create OpenFoam Case
    ctm = uc.convertDocumentUnitsToMeters()

    case = Case.fromBFGeometries(_name, tuple(_BFGeometries),
                                 meshingParameters=_meshParams_, make2dParameters=make2dParams_,
                                 convertToMeters=ctm)

    for reg in refRegions_:
        case.addRefinementRegion(reg)

    if expandBlockMesh_:
        xCount, yCount, zCount = 1, 1, 1
        if case.blockMeshDict.is2dInXDirection:
            xCount = 0
        if case.blockMeshDict.is2dInYDirection:
            yCount = 0
        if case.blockMeshDict.is2dInZDirection:
            zCount = 0

        case.blockMeshDict.expandByCellsCount(xCount, yCount, zCount)

    blockPts = (xyzToPoint(v) for v in case.blockMeshDict.vertices)

    case.save(overwrite=(_run + 1) % 2)


# assign outputs to OUT
OUT = blockPts, case
