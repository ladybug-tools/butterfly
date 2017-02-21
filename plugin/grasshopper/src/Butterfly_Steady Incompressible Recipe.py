# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Butterfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Steady Incompressible Recipe.

-

    Args:
        _turbulenceProp_: Turbulence properties. This values will overwrite default
            values, and can be updated while the solution is running.
        fvSchemes_: Optional input for fvSchemes to overwrite default fvSchemes.
        fvSolution_: Optional input for fvSolution to overwrite default fvSolution.
        residualControl_: residualControl values. This values will overwrite default
            values, and can be updated while the solution is running.
        _relaxationFactors_: relaxationFactors. This values will overwrite default
            values, and can be updated while the solution is running.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Steady Incompressible Recipe"
ghenv.Component.NickName = "SteadyIncomp"
ghenv.Component.Message = 'VER 0.0.03\nFEB_21_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "05::Recipe"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from butterfly.recipe import SteadyIncompressible
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

recipe = SteadyIncompressible(_turbulenceProp_, fvSchemes_, fvSolution_,
                              residualControl_, _relaxationFactors_)

l = len(recipe.quantities)
q = ''.join(q + ' ..... ' if (c + 1) % 4 != 0 and c + 1 != l else q + '\n'
            for c, q in enumerate(recipe.quantities))
