# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Solution Parameter.

    Args:
        _filename: OpenFOAM filename that the values are belong to (e.g.
            blockMeshDict, fvSchemes).
        _values: new values as a valid OpenFOAM (c++) dictionary.
        replace_: Set to True if you want the original dictionary to be replaced
            by new values. Default is False which means the original dictionary
            will be only updated by new values.
    Returns:
        solutionParam: A solution parameter.
"""
ghenv.Component.Name = "Butterfly_Solution Parameter"
ghenv.Component.NickName = "solutionParam"
ghenv.Component.Message = 'VER 0.0.03\nOCT_30_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Solution"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.solution import SolutionParameter
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _filename and _values:
    solutionParam = SolutionParameter.fromCppDictionary(_filename, _values,
                                                     replace_, tRange_)