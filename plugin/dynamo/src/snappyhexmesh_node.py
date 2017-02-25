# assign inputs
_case, _locationInMesh_, _snappyHexMeshDict_, decomposeParDict_, _run = IN
case = None


try:
    from butterfly.surfaceFeatureExtractDict import SurfaceFeatureExtractDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _case and _run:
    
    if _snappyHexMeshDict_:
        assert hasattr(_snappyHexMeshDict_, 'isSolutionParameter'), \
            TypeError(
                '_snappyHexMeshDict_ input is {} and not a SolutionParameter.'
                .format(type(_snappyHexMeshDict_)))
        assert _snappyHexMeshDict_.filename == 'snappyHexMeshDict', \
            TypeError(
                '_snappyHexMeshDict_ input is prepared for {} and not snappyHexMeshDict'
                .format(_snappyHexMeshDict_.filename))
                
        # update values for snappyHexMeshDict
        hasChanged = _case.snappyHexMeshDict.updateValues(_snappyHexMeshDict_.values)
        
        if 'snapControls' in _snappyHexMeshDict_.values:
            if _case.snappyHexMeshDict.extractFeaturesRefineLevel is not None :
                print 'updating snappyHexMeshDict for Explicit Edge Refinement.'
                # change to explicit mode
                _case.snappyHexMeshDict.setFeatureEdgeRefinementToExplicit(
                    _case.projectName,
                    _case.snappyHexMeshDict.extractFeaturesRefineLevel)
                hasChanged = True
        elif _case.snappyHexMeshDict.extractFeaturesRefineLevel is not None:
                print 'updating snappyHexMeshDict for Implicit Edge Refinement.'
                _case.snappyHexMeshDict.setFeatureEdgeRefinementToImplicit()
                hasChanged = True
        
        if hasChanged:
            print 'saving the new snappyHexMeshDict.'
            _case.snappyHexMeshDict.save(_case.projectDir)
        
    if _locationInMesh_:
        _case.snappyHexMeshDict.locationInMesh = tuple(_locationInMesh_)
        _case.snappyHexMeshDict.save(_case.projectDir)
    elif not _case.snappyHexMeshDict.locationInMesh:
        _case.snappyHexMeshDict.locationInMesh = _case.blockMeshDict.center    
        _case.snappyHexMeshDict.save(_case.projectDir)

    # remove result folders if any
    _case.removeResultFolders()
    
    if _case.isPolyMeshSnappyHexMesh:
        # check if meshBlock has been replaced by sHM
        # remove current snappyHexMesh and re-run block mesh
        _case.removeSnappyHexMeshFolders()
        # run blockMesh
        log = _case.blockMesh(overwrite=True)
    
        if not log.success:
            raise Exception("\n --> blockMesh Failed!\n%s" % log.error)                        
    
    if decomposeParDict_:
        _case.decomposeParDict = decomposeParDict_
        _case.decomposeParDict.save(_case.projectDir)
    
    if not _case.snappyHexMeshDict.isFeatureEdgeRefinementImplicit:
        sfe = SurfaceFeatureExtractDict.fromStlFile(_case.projectName, includedAngle=150)
        sfe.save(_case.projectDir)
        log = _case.surfaceFeatureExtract()
        if not log.success:
            raise Exception("\n --> surfaceFeatureExtract Failed!\n%s" % log.error)

    log = _case.snappyHexMesh()
    _case.removeProcessorFolders()
    
    if log.success:
        if _case.getSnappyHexMeshFolders():
            _case.copySnappyHexMesh()
        case = _case
    else:
        raise Exception("\n --> snappyHexMesh Failed!\n%s" % log.error)        

# assign outputs to OUT
OUT = (case,)