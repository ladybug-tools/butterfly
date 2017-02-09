# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Generate fvSchemes based on mesh non-orthogonalities.

-
    Args:
        _quality: Solution quality [0..1]. The quality 0 generates divSchemes
            which is less accurate but more stable. The quality 1 generates a
            divSchemes that are more accurate but less stable. You can start with
            quality 0 and then change it to quality 1 when the solution is
            converging.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        divSchemes: Recommended divSchemes. Use solution parameter to update
            fvSchemes for the solution.
"""

ghenv.Component.Name = "Butterfly_divSchemes library"
ghenv.Component.NickName = "genDivSchemes"
ghenv.Component.Message = 'VER 0.0.03\nFEB_08_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "08::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from butterfly.fvSchemes import FvSchemes
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _quality is not None:
    divSchemes = FvSchemes.divSchemesCollector[_quality%2]
