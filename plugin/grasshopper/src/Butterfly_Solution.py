# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run recipes using OpenFOAM.

-

    Args:
        _case: Butterfly case.
        _orthogonality: Maximum mesh non-orthogonality.
        _run: update fvSchemes.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_Solution"
ghenv.Component.NickName = "solution"
ghenv.Component.Message = 'VER 0.0.01\nSEP_18_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::Solver"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

from subprocess import Popen
import time
from scriptcontext import sticky

ghComponentTimer = sticky['timer']

class Solution(object):
    
    def __init__(self):
       self.__isRunStarted = False
       self.__isRunFinished = False
       self.__process = None
    
    @property
    def isRunning(self):
        if not self.__isRunStarted and not self.__isRunFinished:
            return False
        elif self.__process.poll() is None:
            return True
        else:
            return False
            self.__isRunFinished = True
    
    def run(self):
        batchFile = r"C:\Users\Administrator\butterfly\outdoors_test_3\etc\simpleFoam.bat"
        self.__process = Popen([batchFile])
        self.__isRunStarted = True
        self.__isRunFinished = False
    
    def ToString(self):
        return self.__repr__()
        
    def __repr__(self):
        return "outdoor_analysis::simpleFOAM"


if _run:
    if 's' not in sticky:
        solution = Solution()
        solution.run()
        sticky['s'] = solution
    else:
        solution = sticky['s']
    
    status = solution.isRunning
    
    if solution.isRunning:
        print 'running!'
        ghComponentTimer(ghenv.Component)
    else:
        print 'done!'
        solution = sticky['s']
        del(sticky['s'])
