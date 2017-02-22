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
        _points: A flatten list of points that you're interested to collect the
            values for.
        _fields_: A list of fields such as U, p, k (default: U, p).
        _writeInterval_: Number of intervals between writing the results (default: 1)
    Returns:
        probes: Butterfly probes.
"""

ghenv.Component.Name = "Butterfly_probes"
ghenv.Component.NickName = "probes"
ghenv.Component.Message = 'VER 0.0.03\nFEB_22_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Solution"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.functions import Probes
    import butterfly_grasshopper.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _points:
    probes = Probes()
    c = uc.convertDocumentUnitsToMeters()
    probes.probeLocations = ((p.X * c, p.Y * c, p.Z * c) for p in _points)
    probes.fields = _fields_
    probes.writeInterval = _writeInterval_