# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Set residual control convergance values

    Args:
        _quantities: 
        _values_: Residual control valeus for quantities (default: 1e-5)
        
    Returns:
        residualControl: Residual Control.
"""

ghenv.Component.Name = "Butterfly_residualControl"
ghenv.Component.NickName = "residualControl"
ghenv.Component.Message = 'VER 0.0.03\nFEB_21_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "05::Recipe"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.fvSolution import ResidualControl
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _quantities:
    if not _values_:
        _values_ = (0.0001,)
    
    # match length
    l = len(_quantities)
    values = (_values_[c] if c < len(_values_) else _values_[-1]
        for c, q in enumerate(_quantities))

    residualControl = ResidualControl(
        {key: value for (key, value) in zip(_quantities, values)}
    )
