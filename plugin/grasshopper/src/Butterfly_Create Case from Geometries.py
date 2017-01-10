# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an OpenFOAM Case from geometries.

-

    Args:
        _name: Project name.
        _BFGeometries: List of butterfly geometries for this case.
        _blockMeshDict: A Butterfly BlockMeshDict.
        _globalRefLevel_: A tuple of (min, max) values for global refinment.
        refRegions_: A list of refinement regions.
        _run: Create case from inputs.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        geo: Wind tunnel geometry for visualization.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Create Case from Geometries"
ghenv.Component.NickName = "caseFromGeos"
ghenv.Component.Message = 'VER 0.0.03\nJAN_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly_grasshopper.case import Case
    import butterfly_grasshopper.utilities as util
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _run and _name and _BFGeometries: 
    # create OpenFoam Case
    case = Case.fromBFGeometries(_name, tuple(_BFGeometries),
        meshingParameters=_meshParams_, make2dParameters=make2dParams_)
    
    for reg in refRegions_:
        case.addRefinementRegion(reg)
    
    # make bounding box slightly larger to avoid boundary issues
    case.blockMeshDict.expandUniform(util.tolerance)
    
    case.save(overwrite=(_run + 1) % 2)
