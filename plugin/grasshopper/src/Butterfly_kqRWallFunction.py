# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
kqRWallFunction boundary condition.

-
    Args:
        _value: input value.
        
    Returns:
        kqRWallFunction: kqRWallFunction boundary condition.
"""

ghenv.Component.Name = "Butterfly_kqRWallFunction"
ghenv.Component.NickName = "kqRWallFunction"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "02::BoundaryCondition"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


from butterfly.fields import KqRWallFunction

if _value:
    kqRWallFunction = KqRWallFunction(_value)