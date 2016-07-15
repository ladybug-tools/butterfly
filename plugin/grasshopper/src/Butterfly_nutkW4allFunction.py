# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
nutkWallFunction boundary condition.

-
    Args:
        _value: input value.
        _Cmu_:
        _kappa_:
        _E_:
    Returns:
        nutkWallFunction: nutkWallFunction boundary condition.
"""

ghenv.Component.Name = "Butterfly_nutkW4allFunction"
ghenv.Component.NickName = "nutkWallFunction"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "02::BoundaryCondition"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

from butterfly.fields import NutkWallFunction

if _value:
    nutkWallFunction = NutkWallFunction(_value, _Cmu_, _kappa_, _E_)