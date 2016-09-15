# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Case from wind tunnel.

-

    Args:
        _name: Project name.
        _BFSurfaces: List of butterfly surfaces that will be inside the tunnel.
        _windSpeed: Wind speed in m/s at a the reference height (_refWindHeight_).
        _refWindHeight_: Reference height for wind velocity (default: 10m).
        _windDirection_: Wind direction as Vector3D (default: 0, 1, 0).
        _landscape_: An integer between 0-7 to calculate z0 (roughness).
            0 > '0.0002'  # sea
            1 > '0.005'   # smooth
            2 > '0.03'    # open
            3 > '0.10'    # roughlyOpen
            4 > '0.25'    # rough
            5 > '0.5'     # veryRough
            6 > '1.0'     # closed
            7 > '2.0'     # chaotic
        _globalRefLevel_: A tuple of (min, max) values for global refinment.
        _tunnelPar_: Butterfly tunnel parameters.
        _run: Create wind tunnel case from inputs.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        geo: Wind tunnel geometry for visualization.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Create Case from Tunnel"
ghenv.Component.NickName = "createCaseFromTunnel"
ghenv.Component.Message = 'VER 0.0.01\nSEP_15_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import butterfly.gh.windtunnel
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

import sys
import types

def main():
    wt = butterfly.gh.windtunnel.GHWindTunnel(_name, _BFSurfaces, _windSpeed, _windDirection_, _tunnelPar_,
                      _landscape_, _globalRefLevel_, _refWindHeight_)
    
    for region in refRegions_:
        wt.addRefinementRegion(region)
        
    geo =  wt.boundingbox
    case = wt.toOpenFOAMCase()
    case.createCaseFolders()
    case.populateContents()
    
    return geo, case

if _run and _name and _BFSurfaces and _windSpeed:
        geo, case = main()
