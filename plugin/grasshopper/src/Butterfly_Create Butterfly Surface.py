# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Butterfly surface.

-

    Args:
        _geo: Grasshopper geometries.
        _name: Surface name.
        _boundary_: Boundary for this surface (e.g. Inlet, Outlet, Wall)
        _meshSet_: Grasshopper mesh settings.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        BFSrf: A Buttefly surface.
"""

ghenv.Component.Name = "Butterfly_Create Butterfly Surface"
ghenv.Component.NickName = "createBFSurface"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from butterfly.gh.bfsurface import BFSurface
if _geo and _name:
    BFSrf = BFSurface(_name, _geo, _boundary_, _meshSet_)