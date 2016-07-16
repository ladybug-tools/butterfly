# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Load results for a field in probes.

-

    Args:
        _case: Butterfly case.
        _field: Probes' filed as a string (e.g. p, U).
        
    Returns:
        skippedPoints: List of points that are skipped during the solution.
        values: List of values for the last timestep.
"""

ghenv.Component.Name = "Butterfly_Load Probes"
ghenv.Component.NickName = "loadProbes"
ghenv.Component.Message = 'VER 0.0.01\nJUL_15_2016'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "05::PostProcess"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


from Rhino.Geometry import Point3d, Vector3d

if _case and _field:
    skippedPoints = tuple(Point3d(*p) for p in _case.loadSkippedProbes())
    
    rawValues = _case.loadProbes(_field)
    try:
        values = tuple(Vector3d(*v) for v in rawValues)
    except:
        values = rawValues