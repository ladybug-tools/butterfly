# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Update fvSchemes values based on mesh orthogonalities.

-

    Args:
        _BFObjects: A list of butterfly objects.
        colors_: Optional input for colors to 
    Returns:
        readMe!: Reports, errors, warnings, etc.
        geometries: List of geometries as meshes.
"""

ghenv.Component.Name = "Butterfly_Get Geometry"
ghenv.Component.NickName = "getGeometry"
ghenv.Component.Message = 'VER 0.0.03\nFEB_08_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "08::Etc"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from butterfly_grasshopper.geometry import BFMeshToMesh
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))
else:
    from itertools import chain

def getGeometry(obj):
    """Get Grasshopper geometry from butterfly objects."""
    try:
        return obj.geometry
    except AttributeError:
        try:
            return obj.geometries
        except AttributeError:
            print '{} has no geometry!'.format(type(obj))

if _BFObjects:
    geo = chain.from_iterable(getGeometry(obj) for obj in _BFObjects)
    
    try:
        geo = tuple(geo)
    except TypeError:
        pass
    else:
        if not colors_:
            col = [None] * len(geo)
        else:
            l = len(colors_)
            col = (colors_[c % l] for c, g in enumerate(geo))

        geometries = (BFMeshToMesh(g, c) for g, c in zip(geo, col))
