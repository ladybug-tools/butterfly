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
        _nonOrthogonality: Maximum mesh non-orthogonality as an integer.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        fvSchemes: Recommended fvSchemes. Use solution parameter to update fvSchemes
            for the solution.
"""

ghenv.Component.Name = "Butterfly_FvSchemes from Non-orthogonality"
ghenv.Component.NickName = "genFvSchemes"
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

if  _nonOrthogonality:
    fvSchemes = FvSchemes.fromMeshOrthogonality(_nonOrthogonality)
