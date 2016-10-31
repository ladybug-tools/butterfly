# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Inside/Ouside region refinement.

-

    Args:
        _levels_0: (d, l) values for level where d is distance of region and 
            l is level of refinement. 'levels' specifies per distance to the
            surface the wanted refinement level.
        
    Returns:
        distanceRefMode: Refinement mode.
"""

ghenv.Component.Name = "Butterfly_DistanceRefinementMode"
ghenv.Component.NickName = "distRefMode"
ghenv.Component.Message = 'VER 0.0.03\nOCT_30_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:
    from butterfly.refinementRegion import Distance
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

_level = [tuple(i) for i in [_levels_0, _levels_1] if i]

if _level:
    distanceRefMode = Distance(_level)