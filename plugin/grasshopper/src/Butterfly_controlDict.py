# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Set parameters for runDict

    Args:
        _startTime_: Start timestep (default: 0)
        _endTime_: End timestep (default: 1000)
        _writeInterval_: Number of intervals between writing the results (default: 100)
        _writeCompression_: Set to True if you want the results to be compressed
            before being written to your machine (default: False).
        _purgeWrite_: Number of results folder to be kept. 0 means that all the
            result folder will be kept (default: 0).
        funcObjects_: A list of OpenFOAM function objects. Use functionObject
            component to create a butterfly function object from a cpp dictionary.
    Returns:
        controlDict: Butterfly controlDict.
"""
ghenv.Component.Name = "Butterfly_controlDict"
ghenv.Component.NickName = "controlDict"
ghenv.Component.Message = 'VER 0.0.03\nMAR_12_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "06::Solution"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.controlDict import ControlDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


cd = ControlDict()
if _startTime_ is not None:
    cd.startTime = _startTime_

if _endTime_ is not None:
    cd.endTime = _endTime_

if _writeInterval_ is not None:
    cd.writeInterval = _writeInterval_

if _writeCompression_ is not None:
    cd.writeCompression = _writeCompression_

if _purgeWrite_ is not None:
    cd.purgeWrite = _purgeWrite_

if funcObjects_ and funcObjects_[0] is not None:
    cd.functions = funcObjects_

controlDict = cd