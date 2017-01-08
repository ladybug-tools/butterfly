# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Load mesh from the case for preview.

-

    Args:
        _case: Butterfly case.
        innerMesh_: Set to True to load inner mesh. Default is False which means
            the component only loads the mesh for boundary faces.
        _load: Load mesh.
        
    Returns:
        mesh: OpenFOAM mesh
"""

ghenv.Component.Name = "Butterfly_Load Mesh"
ghenv.Component.NickName = "loadMesh"
ghenv.Component.Message = 'VER 0.0.03\nJAN_08_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

if _case and _load:
    mesh = _case.loadMesh(innerMesh_)