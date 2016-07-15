# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Update fvSchemes values based on mesh orthogonalities.

-

    Args:
        _case: Butterfly case.
        _orthogonality: Maximum mesh non-orthogonality.
        _run: update fvSchemes.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Update FvSchemes"
ghenv.Component.NickName = "updateFvSchemes"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

if _case and _orthogonality and _run:
    # update fvSchemes
    _case.setFvSchemesfromMeshOrthogonality(_orthogonality)
    _case.fvSchemes.save(_case.projectDir)
    print _case.fvSchemes
    case = _case