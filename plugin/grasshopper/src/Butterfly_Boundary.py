# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a custom boundary.

-

    Args:
        _bType_: Boundary type (e.g wall, patch, etc.)
        _U_: Boundary condition for U.
        _p_: Boundary condition for P.
        _k_: Boundary condition for k.
        _epsilon: Boundary condition for epsilon.
        _nut_: Boundary condition for nut.
    Returns:
        boundary: Buttefly custom boundary.
"""

ghenv.Component.Name = "Butterfly_Boundary"
ghenv.Component.NickName = "boundary"
ghenv.Component.Message = 'VER 0.0.03\nFEB_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "01::Boundary"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly import boundarycondition
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

_bType_ = 'patch' if not _bType_ else _bType_

boundary = boundarycondition.BoundaryCondition(
    _bType_, U=_U_, p=_p_, k=_k_, epsilon=_epsilon_,
    nut=_nut_, alphat=_alphat_, p_rgh=_p_rgh_, T=_T_
)

boundary = boundary.duplicate()