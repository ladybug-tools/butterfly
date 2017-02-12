# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Update blockMeshDict.

-

    Args:
        _case: A butterfly case.
        _points: A list of 8 point.
        xAxis_: Optional vector to set xAxis for blockMeshDict (default: (1, 0, 0)).
        _run: update blockMeshDict and save it folder.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Update blockMeshDict"
ghenv.Component.NickName = "updateBMDict"
ghenv.Component.Message = 'VER 0.0.03\nFEB_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "4"
if _run and _case and any(p is not None for p in _points) and xAxis_:
    
    _case.blockMeshDict.updateVertices(
        tuple((p.X, p.Y, p.Z) for p in _points), (xAxis_.X, xAxis_.Y, xAxis_.Z))
    _case.blockMeshDict.save(_case.projectDir)
    case = _case