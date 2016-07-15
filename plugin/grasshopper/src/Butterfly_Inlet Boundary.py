# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an inlet boundary with uniform velocity value.

-

    Args:
        _velocityVec: Velocity vector.
        _refLevels_: A tuple of (min, max) values for refinement levels.
    Returns:
        inletBoundary: Buttefly inlet boundary.
"""

ghenv.Component.Name = "Butterfly_Inlet Boundary"
ghenv.Component.NickName = "inlet"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "01::Boundary"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

from butterfly import boundarycondition as bc
from butterfly.fields import FixedValue

#import butterfly
#reload(butterfly)
#reload(butterfly.boundarycondition)
#reload(butterfly.fields)

if _velocityVec:
    _velocityVec = FixedValue(str(tuple(_velocityVec)).replace(',', '')) \
                   if _velocityVec \
                   else None

    inletBoundary = bc.FixedInletBoundaryCondition(refLevels=_refLevels_, u=_velocityVec)
