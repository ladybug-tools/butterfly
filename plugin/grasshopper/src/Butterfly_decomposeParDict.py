# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
decomposeParDict. Dictionary for parallel runs.

-

    Args:
        _mode_: Decompose mode (0: scotch, 1: simple).
    Returns:
        locationRefMode: Refinement mode.
"""

ghenv.Component.Name = "Butterfly_decomposeParDict"
ghenv.Component.NickName = "decomposeParDict"
ghenv.Component.Message = 'VER 0.0.03\nJAN_08_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::Etc"
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

def modifyComponentInput(index, name, nickName, description):
    """Modify input parameter of the component."""
    ghenv.Component.Params.Input[index].Name = name
    ghenv.Component.Params.Input[index].NickName = nickName
    ghenv.Component.Params.Input[index].Description = description
    ghenv.Component.Params.OnParametersChanged()

if not _mode_:
    modifyComponentInput(index=1, name='_numOfCpus_', nickName='_numOfCpus_',
                         description='Number of CPUs (default: 2).')
    modifyComponentInput(index=2, name='.', nickName='.', description='.')
    try:
        numberOfSubdomains = _numOfCpus_[0]
    except:
        numberOfSubdomains = 2
 
    decomposeParDict = DecomposeParDict.scotch(numberOfSubdomains)
else:
    modifyComponentInput(index=1, name='_XYZDiv_', nickName='_XYZDiv_',
        description='Number of subdomains in x, y, z as a list. default: (2, 1, 1)')
    modifyComponentInput(index=2, name='_delta_', nickName='_delta_',
                     description='Cell skew factor (default: 0.001).')
    
    try:
        x, y, z = _XYZDiv_
    except:
        x, y, z = 2, 1, 1
    
    decomposeParDict = DecomposeParDict.simple((x, y, z), _delta_)