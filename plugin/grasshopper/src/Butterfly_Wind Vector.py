# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Butterfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Wind vector.

-

    Args:
        _windSpeed: Wind speed in m/s at a the reference height (_refWindHeight_).
        _windDirection_: Wind direction as Vector3D (default: 0, 1, 0).
    Returns:
        windVector: Wind Vector.
"""

ghenv.Component.Name = "Butterfly_Wind Vector"
ghenv.Component.NickName = "WindVector"
ghenv.Component.Message = 'VER 0.0.03\nFEB_14_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

if _windSpeed and _windDirection_:
    try:
        _windDirection_.Unitize()
        windVector = _windSpeed * _windDirection_
    except AttributeError:
        # dynamo
        nv = _windDirection_.Normalized();
        windVector = nv.Scale(_windSpeed);