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
        refRegions_: A list of refinement regions.
        make2dParams_: Butterfly parameters to make a 2d wind tunnel.
        _meshParams_: Butterfly meshing parameters. You can set-up meshing parameters
            also on the blockMesh and snappyHexMesh components to overwrite this
            settings. Use this input to set up the meshing parameters if you are
            not running the meshing locally.
        expandBlockMesh_: Butterfly by default expands the mesh by one cell to
            ensure snappyHexMesh will snap to extrior surfaces. You can set the
            expand to off or overwrite the vertices using update blockMeshDict
            component.
        _run: Create case from inputs.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        geo: Wind tunnel geometry for visualization.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Create Case from Geometries"
ghenv.Component.NickName = "caseFromGeos"
ghenv.Component.Message = 'VER 0.0.03\nFEB_26_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly_grasshopper.case import Case
    from butterfly_grasshopper.geometry import xyzToPoint
    import butterfly_grasshopper.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from food4Rhino!' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))


if _run and _name and _BFGeometries: 
    # create OpenFoam Case
    ctm = uc.convertDocumentUnitsToMeters()
    
    case = Case.fromBFGeometries(_name, tuple(_BFGeometries),
        meshingParameters=_meshParams_, make2dParameters=make2dParams_,
        convertToMeters=ctm)
    
    for reg in refRegions_:
        case.addRefinementRegion(reg)
    
    if expandBlockMesh_:
        xCount, yCount, zCount = 1, 1, 1
        if case.blockMeshDict.is2dInXDirection:
            xCount = 0
        if case.blockMeshDict.is2dInYDirection:
            yCount = 0
        if case.blockMeshDict.is2dInZDirection:
            zCount = 0
        
        case.blockMeshDict.expandByCellsCount(xCount, yCount, zCount)
    
    blockPts = (xyzToPoint(v) for v in case.blockMeshDict.vertices)
    
    case.save(overwrite=(_run + 1) % 2)
