# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a wall boundary.

-

    Args:
        _refLevels_: A tuple of (min, max) values for refinement levels.
    Returns:
        wallBoundary: Buttefly wall boundary.
"""

ghenv.Component.Name = "Butterfly_Wall Boundary"
ghenv.Component.NickName = "wall"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "01::Boundary"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import butterfly
from butterfly import boundarycondition

#reload(butterfly)
#reload(butterfly.boundarycondition)

wallBoundary = boundarycondition.IndoorWallBoundaryCondition(refLevels=_refLevels_)
