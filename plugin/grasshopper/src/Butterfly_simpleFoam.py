# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Butterfly simpleFoam. This component will change to a recipe in the next release.

-

    Args:
        _case: Butterfly case.
        _controlDict_: Optional modified controlDict. controlDict component is under 6::etc.
        _residualControl_: Optional residualControl. residualControl component is under 6::etc.
        _probes_: Optional probes. probes component is under 6::etc.
        alternataeOFDicts_: A list of OpenFOAM dictionaries to overwrite butterfly 
        _run: Run simpleFoam.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_simpleFoam"
ghenv.Component.NickName = "simpleFoam"
ghenv.Component.Message = 'VER 0.0.01\nJUL_14_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "04::Solver"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

if _case:
    if alternataeOFDicts_:
        raise NotImplementedError('alternataeOFDicts_ will let you to use alternate OpenFOAM dictionaries. Coming soon!')
    
    if _controlDict_ and hasattr(_controlDict_, 'startTime'):
        _case.controlDict.startTime = _controlDict_.startTime
        _case.controlDict.endTime = _controlDict_.endTime
        _case.controlDict.writeInterval = _controlDict_.writeInterval
        _case.controlDict.writeCompression = _controlDict_.writeCompression
        _case.controlDict.save(_case.projectDir)
    
    if _probes_:
        # assign probe to case - it will be also included in controlDict
        _case.probes = _probes_
        _case.probes.save(_case.projectDir)
        _case.controlDict.save(_case.projectDir)
        
    if _residualControl_ and hasattr(_residualControl_, 'p'):
        _case.fvSolution.residualControl(p=_residualControl_.p,
                                         U=_residualControl_.U,
                                         k=_residualControl_.k,
                                         epsilon=_residualControl_.epsilon)
        
        _case.fvSolution.save(_case.projectDir)
        
if _case and _run:
    _case.copySnappyHexMesh()
    _case.renameSnappyHexMeshFolders()
    success, err = _case.simpleFoam()
    _case.renameSnappyHexMeshFolders()

    if success:
        case = _case
    else:
        # rename the folders back
        raise Exception("\n --> OpenFOAM command Failed!%s" % err)   
    