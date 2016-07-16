# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Butterfly probes

    Args:
        _pts: A flatten list of points that you're interested to collect the values for.
        _fields_: A list of fields such as U, p, k (default: U, p).
        _writeInterval_: Number of intervals between writing the results (default: 1)
    Returns:
        probes: Butterfly probes.
"""

ghenv.Component.Name = "Butterfly_probes"
ghenv.Component.NickName = "probes"
ghenv.Component.Message = 'VER 0.0.01\nJUL_15_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    #import butterfly
    #reload(butterfly)
    #reload(butterfly.functions)
    from butterfly.functions import Probes
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _pts:
    probes = Probes()
    probes.probeLocations = _pts
    probes.fields = _fields_
    probes.writeInterval = _writeInterval_