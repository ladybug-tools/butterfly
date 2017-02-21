# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Simple decomposeParDict. Dictionary for parallel runs.

-

    Args:
        _XYZDiv_: Number of subdomains in x, y, z as a list (default: (2, 1, 1)).
        _delta_: Cell skew factor (default: 0.001).
    Returns:
        decomposeParDict: decomposeParDict.
"""

ghenv.Component.Name = "Butterfly_decomposeParDict simple"
ghenv.Component.NickName = "decomposeParDict_simple"
ghenv.Component.Message = 'VER 0.0.03\nFEB_21_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "08::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.decomposeParDict import DecomposeParDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

try:
    x, y, z = _XYZDiv_
except:
    x, y, z = 2, 1, 1

decomposeParDict = DecomposeParDict.simple((x, y, z), _delta_)
