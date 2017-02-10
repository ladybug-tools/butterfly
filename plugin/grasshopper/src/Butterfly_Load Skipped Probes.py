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
        _solution: A Butterfly solution.
        
    Returns:
        skippedPoints: List of points that are skipped during the solution.
"""

ghenv.Component.Name = "Butterfly_Load Skipped Probes"
ghenv.Component.NickName = "loadSkippedProbes"
ghenv.Component.Message = 'VER 0.0.03\nFEB_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::PostProcess"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

from Rhino.Geometry import Point3d

if _solution:
    try:
        pts = _solution.skippedProbes()
    except AssertionError as e:
        raise ValueError('{}.\nDid you run the solution before loading the probes?'.format(e))

    try:
        skippedProbes = tuple(Point3d(*v) for v in pts)
    except:
        skippedProbes = pts