# assign inputs
_case, _cellSizeXYZ_, _gradXYZ_, _overwrite_, _run = IN
case = None

if _case and _run:
    # remove current snappyHexMeshFolders
    if _overwrite_:
        _case.removeSnappyHexMeshFolders()
    # run blockMesh
    if _cellSizeXYZ_:
        _case.blockMeshDict.nDivXYZByCellSize(
            (_cellSizeXYZ_.X, _cellSizeXYZ_.Y, _cellSizeXYZ_.Z))
    if _gradXYZ_:
        _case.blockMeshDict.grading = _gradXYZ_
    if _cellSizeXYZ_ or _gradXYZ_:
        _case.blockMeshDict.save(_case.projectDir)
    
    log = _case.blockMesh(overwrite=True)
    if log.success:
        case = _case
    else:
        raise Exception("\n\n\nButterfly failed to run OpenFOAM command!\n%s" % log.error)


# assign outputs to OUT
OUT = (case,)