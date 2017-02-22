# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
blockMesh

-

    Args:
        _case: Butterfly case.
        _cellSizeXYZ_: Cell size in (x, y, z) as a tuple (default: length / 5).
            This value updates number of divisions in blockMeshDict.
        _gradXYZ_: A simpleGrading (default: simpleGrading(1, 1, 1)). This value
            updates grading in blockMeshDict.
        _overwrite_: Remove current snappyHexMesh folders from the case if any (default: True). 
        _run: run blockMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_blockMesh"
ghenv.Component.NickName = "blockMesh"
ghenv.Component.Message = 'VER 0.0.03\nFEB_22_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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
