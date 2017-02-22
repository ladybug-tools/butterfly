# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Solution Parameters.

    Args:
        controlDict_: controlDict.
        residualControl_: residualControl.
        probes_: probes.
        additionalParams_: List of solution parameters. Use solutionParameter
            component to create solutionParams.
    Returns:
        solutionParams: A list of solution parameters.
"""
ghenv.Component.Name = "Butterfly_Solution Parameters"
ghenv.Component.NickName = "solutionParams"
ghenv.Component.Message = 'VER 0.0.03\nFEB_22_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Solution"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
     from butterfly.solution import SolutionParameter
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if controlDict_:
    controlDict_ = SolutionParameter.fromCppDictionary('controlDict', str(controlDict_))

if probes_:
    probes_ = SolutionParameter.fromCppDictionary('probes', str(probes_))


params = [controlDict_, probes_] + additionalParams_

solutionParams = (p for p in params if p)
