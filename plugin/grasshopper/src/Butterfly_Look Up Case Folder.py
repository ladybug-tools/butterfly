# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Butterfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Look Up Case Folder.

-

    Args:
        _case: Butterfly case.
        fullpath_: Set to True to get fullpath for the files.
    Returns:
        zero: Files in zero folder.
        constant: Files in constant folder.
        triSurface: Files in constant/triSurface folder.
        system: Files in system folder.
"""

ghenv.Component.Name = "Butterfly_Look Up Case Folder"
ghenv.Component.NickName = "lookUpCaseFolder"
ghenv.Component.Message = 'VER 0.0.03\nFEB_08_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "08::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

def listfiles(folder, fullpath):
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            if fullpath:
                yield os.path.normpath(os.path.join(folder, f))
            else:
                yield os.path.normpath(f)

if _case:
    if isinstance(_case, str):
        projectDir = _case.replace('\\\\','/').replace('\\','/')
    else:
        try:
            projectDir = _case.projectDir
        except:
            raise ValueError('Invaild input for _case.')
    
    files = []
    for p in ('0', 'constant', 'constant/triSurface', 'system'):
        files.append(listfiles(os.path.join(projectDir, p), fullpath_))
    
    zero, constant, triSurface, system = files
