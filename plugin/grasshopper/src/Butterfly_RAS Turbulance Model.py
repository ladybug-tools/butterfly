# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Reynolds-averaged simulation (RAS) turbulence model.

Read more: http://cfd.direct/openfoam/user-guide/turbulence/
Watch this: https://www.youtube.com/watch?v=Eu_4ppppQmw

    Args:
        _RASModel_: Name of RAS turbulence model (default: RNGkEpsilon).
            Incompressible RAS turbulence models.
                LRR, LamBremhorstKE, LaunderSharmaKE, LienCubicKE,
                LienLeschziner, RNGkEpsilon, SSG, ShihQuadraticKE,
                SpalartAllmaras, kEpsilon, kOmega, kOmegaSSTSAS, kkLOmega,
                qZeta, realizableKE, v2f
            Compressible RAS turbulence models.
                LRR, LaunderSharmaKE, RNGkEpsilon, SSG, SpalartAllmaras,
                buoyantKEpsilon, kEpsilon, kOmega, kOmegaSSTSAS,
                realizableKE, v2f
        _turbulence_: Boolean switch to turn the solving of turbulence
            modelling on/off (default: True).
        _printCoeffs_: Boolean switch to print model coeffs to terminal at
            simulation start up (default: True).
"""

ghenv.Component.Name = "Butterfly_RAS Turbulance Model"
ghenv.Component.NickName = "RAS"
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


RAS = TurbulenceProperties.RAS(_RASModel_, _turbulence_, _printCoeffs_)