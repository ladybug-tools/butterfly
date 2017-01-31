# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Butterfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
snappyHexMesh

-

    Args:
        _case: Butterfly case.
        _locationInMesh_: A point 3d to locate the volume that should be meshed. By default center of the boundingbox will be used.
        _snappyHexMeshDict_: optional modified snappyHexMeshDict.
        decomposeParDict_: decomposeParDict for running snappyHexMesh in parallel.
        _run: run snappyHexMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_snappyHexMesh"
ghenv.Component.NickName = "snappyHexMesh"
ghenv.Component.Message = 'VER 0.0.03\nJAN_31_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


try:
    from butterfly.surfaceFeatureExtractDict import SurfaceFeatureExtractDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _case and _run:
    
    if _snappyHexMeshDict_:
        assert hasattr(_snappyHexMeshDict_, 'locationInMesh'), \
            TypeError(
                '_snappyHexMeshDict_ input is {} and not a SnappyHexMeshDict.'
                .format(type(_snappyHexMeshDict_)))
            
        # update values for snappyHexMeshDict
        _case.snappyHexMeshDict.castellatedMesh = _snappyHexMeshDict_.castellatedMesh
        _case.snappyHexMeshDict.snap = _snappyHexMeshDict_.snap
        _case.snappyHexMeshDict.addLayers = _snappyHexMeshDict_.addLayers
        _case.snappyHexMeshDict.nCellsBetweenLevels = str(_snappyHexMeshDict_.nCellsBetweenLevels)
        _case.snappyHexMeshDict.maxGlobalCells = str(_snappyHexMeshDict_.maxGlobalCells)
        if _snappyHexMeshDict_.extractFeaturesRefineLevel:
            print 'updating snappyHexMeshDict for Implicit Edge Refinement.'
            # change to explicit mode
            _case.snappyHexMeshDict.setFeatureEdgeRefinementToExplicit(
                _case.projectName, _snappyHexMeshDict_.extractFeaturesRefineLevel)
        
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
    
    if log.success:
        if _case.getSnappyHexMeshFolders():
            _case.copySnappyHexMesh()
        case = _case
    else:
        raise Exception("\n --> snappyHexMesh Failed!\n%s" % log.error)        