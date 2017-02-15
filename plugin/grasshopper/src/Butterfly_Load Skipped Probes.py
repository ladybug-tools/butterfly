# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Load results for a field in probes.

-

    Args:
        _solution: A Butterfly solution.
        
    Returns:
        skippedPoints: List of points that are skipped during the solution.
"""

ghenv.Component.Name = "Butterfly_Load Skipped Probes"
ghenv.Component.NickName = "loadSkippedProbes"
ghenv.Component.Message = 'VER 0.0.03\nFEB_15_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::PostProcess"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:
    from butterfly_grasshopper.geometry import xyzToPoint
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'


if _solution:
    try:
        pts = _solution.skippedProbes()
    except AssertionError as e:
        raise ValueError('{}.\nDid you run the solution before loading the probes?'.format(e))
    except AttributeError:
        raise ValueError('{} is not a butterfly Solution.'.format(_solution))
    try:
        skippedProbes = tuple(xyzToPoint(v) for v in pts)
    except:
        skippedProbes = pts