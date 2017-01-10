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
ghenv.Component.Message = 'VER 0.0.03\nJAN_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


if _case and _run:

    if _snappyHexMeshDict_ and hasattr(_snappyHexMeshDict_, 'locationInMesh'):
        # update values for snappyHexMeshDict
        _case.snappyHexMeshDict.castellatedMesh = _snappyHexMeshDict_.castellatedMesh
        _case.snappyHexMeshDict.snap = _snappyHexMeshDict_.snap
        _case.snappyHexMeshDict.addLayers = _snappyHexMeshDict_.addLayers
        _case.snappyHexMeshDict.maxGlobalCells = str(_snappyHexMeshDict_.maxGlobalCells)
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
            raise Exception("\n --> OpenFOAM command Failed!\n%s" % log.error)                        
    
    if decomposeParDict_:
        _case.decomposeParDict = decomposeParDict_
        _case.decomposeParDict.save(_case.projectDir)
    
    log = _case.snappyHexMesh()
    
    if log.success:
        if _case.getSnappyHexMeshFolders():
            _case.copySnappyHexMesh()
        case = _case
    else:
        raise Exception("\n --> OpenFOAM command Failed!\n%s" % log.error)        