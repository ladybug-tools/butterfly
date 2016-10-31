# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Large eddy simulation (LES) modelling.

Read more: http://cfd.direct/openfoam/user-guide/turbulence/
Watch this: https://www.youtube.com/watch?v=Eu_4ppppQmw

    Returns:
        laminar: Laminar model
"""

ghenv.Component.Name = "Butterfly_Laminar Turbulance Model"
ghenv.Component.NickName = "leminar"
ghenv.Component.Message = 'VER 0.0.03\nOCT_30_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "04::Turbulance"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from butterfly.turbulenceProperties import TurbulenceProperties
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


laminar = TurbulenceProperties.laminar()