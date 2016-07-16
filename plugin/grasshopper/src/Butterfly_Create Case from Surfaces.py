# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an OpenFOAM Case from surfaces.

-

    Args:
        _name: Project name.
        _BFSurfaces: List of butterfly surfaces for this case.
        _blockMeshDict: A Butterfly BlockMeshDict.
        _globalRefLevel_: A tuple of (min, max) values for global refinment.
        _tunnelPar_: Butterfly tunnel parameters.
        _run: Create case from inputs.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        geo: Wind tunnel geometry for visualization.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Create Case from Surfaces"
ghenv.Component.NickName = "createCaseFromSurfaces"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from butterfly.gh.core import Case
#import butterfly
#reload(butterfly.core)
#reload(butterfly.controlDict)
#reload(butterfly.gh.core)

if _run and _name and _BFSurfaces and _blockMeshDict: 
    # create OpenFoam Case
    case = Case(_name, _BFSurfaces, _blockMeshDict, _globalRefLevel_,
                _blockMeshDict.center, isSnappyHexMesh=True)
    
    case.createCaseFolders()
    case.populateContents()
