# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
snappyHexMesh

-

    Args:
        _case: Butterfly case.
        _locationInMesh_: A point 3d to locate the volume that should be meshed. By default center of the boundingbox will be used.
        _snappyHexMeshDict_: optional modified snappyHexMeshDict.
        _run: run snappyHexMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_snappyHexMesh"
ghenv.Component.NickName = "snappyHexMesh"
ghenv.Component.Message = 'VER 0.0.01\nSEP_18_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

if _case:
    if not _locationInMesh_:
        _locationInMesh_ = _case.blockMeshDict.center
    else:
        _locationInMesh_ = tuple(_locationInMesh_)

    if _snappyHexMeshDict_ and hasattr(_snappyHexMeshDict_, 'locationInMesh'):
        # update values for snappyHexMeshDict
        _case.snappyHexMeshDict.castellatedMesh = _snappyHexMeshDict_.castellatedMesh
        _case.snappyHexMeshDict.snap = _snappyHexMeshDict_.snap
        _case.snappyHexMeshDict.addLayers = _snappyHexMeshDict_.addLayers
        _case.snappyHexMeshDict.maxGlobalCells = str(_snappyHexMeshDict_.maxGlobalCells)
        
    _case.snappyHexMeshDict.locationInMesh = _locationInMesh_
    
    if _run:
        _case.snappyHexMeshDict.save(_case.projectDir)
        if _case.getSnappyHexMeshFolders():
            _case.copySnappyHexMesh()
        success, err, p = _case.snappyHexMesh()
        if success:
            case = _case
        else:
            raise Exception("\n --> OpenFOAM command Failed!%s" % err)        