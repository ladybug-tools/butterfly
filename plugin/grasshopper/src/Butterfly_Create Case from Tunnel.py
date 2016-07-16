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
        _windSpeed: Wind speed in m/s.
        _windDirection_: Wind direction as Vector3D (default: 0, 1, 0).
        _landscape_: An integer between 0-7 to calculate z0 (roughness).
            0: '0.0002'  # sea
            1: '0.005'   # smooth
            2: '0.03'    # open
            3: '0.10'    # roughlyOpen
            4: '0.25'    # rough
            5: '0.5'     # veryRough
            6: '1.0'     # closed
            7: '2.0'     # chaotic
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
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import butterfly, butterfly.gh.windtunnel
import sys
import types

def reload_package(root_module):
    package_name = root_module.__name__

    # get a reference to each loaded module
    loaded_package_modules = dict([
        (key, value) for key, value in sys.modules.items() 
        if key.startswith(package_name) and isinstance(value, types.ModuleType)])

    # delete references to these loaded modules from sys.modules
    for key in loaded_package_modules:
        del sys.modules[key]

    # load each of the modules again; 
    # make old modules share state with new modules
    for key in loaded_package_modules:
        # print 'loading %s' % key
        newmodule = __import__(key)
        oldmodule = loaded_package_modules[key]
        oldmodule.__dict__.clear()
        oldmodule.__dict__.update(newmodule.__dict__)

def main():
    wt = butterfly.gh.windtunnel.GHWindTunnel(_name, _BFSurfaces, _windSpeed, _windDirection_, _tunnelPar_,
                      _landscape_, _globalRefLevel_)
    geo =  wt.boundingbox
    case = wt.toOpenFOAMCase()
    case.createCaseFolders()
    case.populateContents()
    
    return geo, case


# This is a hack. I should get it fixed soon. Read here for more:
# https://github.com/mostaphaRoudsari/Butterfly/issues/33

if _run and _name and _BFSurfaces and _windSpeed:
    try:
        geo, case = main()
    except TypeError:
        print "reloading butterfly! If the component complained about importing functions" \
            " simply re-run the component. This bug will be fixed in the next releases."
        reload_package(butterfly)
        geo, case = main()
