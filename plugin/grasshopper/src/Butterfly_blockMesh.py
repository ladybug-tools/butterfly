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
        _purge_: Remove current snappyHexMesh folders from the case if any (default: False). 
        _run: run blockMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_blockMesh"
ghenv.Component.NickName = "blockMesh"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

if _case and _run:
    # remove current snappyHexMeshFolders
    if _purge_:
        _case.removeSnappyHexMeshFolders()
    # run blockMesh
    success, err = _case.blockMesh(removeContent=True)
    if success:
        case = _case
    else:
        raise Exception("\n --> OpenFOAM command Failed!%s" % err)