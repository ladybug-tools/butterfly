# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Sample the results for a case.
Use this component yo load the results for a case that you have ran already. 

-

    Args:
        _solution: Butterfly Solution, Case or fullpath to the case folder.
        _name: A name for this smaple. The results will be saved under postProcessing
            folder under <name>_<field>_sampleDict/<latestTime>/<name>_<field>.xy
        _points: A list of flattened points to be sampled.
        _field: Filed of interest as a string (e.g. p, U).
        _run: Set to true to run the sample.
    Returns:
        probes: List of probes as points. This list should be identical to the input
            _points if there is no skipped points.
        values: List of values as numbers or vectors.
"""

ghenv.Component.Name = "Butterfly_Sample Case"
ghenv.Component.NickName = "sampleCase"
ghenv.Component.Message = 'VER 0.0.03\nFEB_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::PostProcess"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

from Rhino.Geometry import Point3d, Vector3d
import os


if _solution and _name and any(p is not None for p in _points) and _field and _run:
    
    assert hasattr(_solution, 'sample'), \
        'Invalid Input: <{}> is not a valid Butterfly Case or Solution.'.format(_solution)
    
    points = ((pt.X, pt.Y, pt.Z) for pt in _points)
    res = _solution.sample(_name, points, _field)
    
    if res:
        probes = (Point3d(*p) for p in res.probes)
        
        if isinstance(res.values[0], float) == 1:
            values = res.values
        else:
            values = (Vector3d(*v) for v in res.values)