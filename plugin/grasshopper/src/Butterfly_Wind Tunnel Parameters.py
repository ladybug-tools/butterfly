# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Wind tunnel parameters.

-

    Args:
        _windwardX_: Multiplier value for windward extension (default: 3).
        _topX_: Multiplier value for top extension (default: 3).
        _sideX_: Multiplier value for side extension (default: 2).
        _leewardX_: Multiplier value for leeward extension (default: 15).
        _nDivXYZ_: Number of Block divisions in X, Y and Z. You can use a point component to input values.
        _gradXYZ_: Grading value for X, Y and Z. You can use a point component to input values.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        tunnelPar: Tunnel Parameters
"""

ghenv.Component.Name = "Butterfly_Wind Tunnel Parameters"
ghenv.Component.NickName = "WindTunnelPar"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


from butterfly.windtunnel import TunnelParameters

tunnelPar = TunnelParameters(_windwardX_, _topX_, _sidesX_, _leewardX_,
                             _nDivXYZ_, _gradXYZ_)