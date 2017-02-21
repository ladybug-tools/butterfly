# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Set relaxtionFactors values

    Args:
        _quantities: 
        _values: relaxtionValues
        
    Returns:
        relaxationFactors: Relaxation factors.
"""

ghenv.Component.Name = "Butterfly_relaxtionFactors"
ghenv.Component.NickName = "relaxtionFactors"
ghenv.Component.Message = 'VER 0.0.03\nFEB_21_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "05::Recipe"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.fvSolution import RelaxationFactors
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


if _quantities and _values:
    
    assert len(_quantities) == len(_values), \
        'Length of quantities [%d] must be equal to the length of values [%d].' \
        % (len(_quantities), len(_values))

    relaxationFactors = RelaxationFactors(
        {key: value for (key, value) in zip(_quantities, _values)}
    )