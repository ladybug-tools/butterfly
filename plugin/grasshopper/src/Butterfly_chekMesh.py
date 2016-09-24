# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
chekMesh

-

    Args:
        _case: Butterfly case.
        _run: run chekMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
        maxNonOrthogonality: Maximum mesh non-orthogonality. Use this value to update fvSchemes.
"""

ghenv.Component.Name = "Butterfly_chekMesh"
ghenv.Component.NickName = "chekMesh"
ghenv.Component.Message = 'VER 0.0.02\nSEP_23_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

if _case and _run:
    maxNonOrthogonality, avgNonOrthogonality = _case.calculateMeshOrthogonality()
    print "Mesh non-orthogonality max: {}, Mesh non-orthogonality average: {}".format(maxNonOrthogonality, avgNonOrthogonality)
    case = _case