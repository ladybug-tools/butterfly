# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an OpenFOAM Case from an existing case in a local folder.

-

    Args:
        name_: Optional new name to change the name of the case.
        _folder: Fullpath to an OpenFoam case folder.
        _run: Create case from inputs.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Create Case from Folder"
ghenv.Component.NickName = "caseFromFolder"
ghenv.Component.Message = 'VER 0.0.03\nFEB_21_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "00::Create"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from butterfly_grasshopper.case import Case
    import butterfly_grasshopper.unitconversion as uc
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _folder and _run: 
    # create OpenFoam Case
    case = Case.fromFolder(_folder, name_, 1.0 / uc.convertDocumentUnitsToMeters())
    case.save(overwrite=False)