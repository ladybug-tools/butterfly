# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Set parameters for snappyHexMeshDict.
Read more about snappyHexMeshDict here:
    https://openfoamwiki.net/images/f/f0/Final-AndrewJacksonSlidesOFW7.pdf


    Args:
        _meshQuality_: Use 0-2 to auto generate the parameters for meshQualityControls
        _castellatedMesh_: Set to True to castellated mesh (default: True).
        _snap_: Set to True to snap mesh to the surfaces (default: True).
        _addLayers_: Set to True to push mesh away from surfaces and add layers (default: False).
        _maxGlobalCells_: An intger for the maximum number of global cells (default: 2000000).
        _features_: Attach the output of the "create case from wind tunnel component".
        note that, this can only be used for explicit meshing feature, if you want to use implicit meshing, 
        there's no need to attach anything.
        _level_: An integer for the extract features refinement (default: 1).
        
    Returns:
        snappyHexMeshDict: Butterfly snappyHexMeshDict.
"""

ghenv.Component.Name = "Butterfly_snappyHexMeshDict"
ghenv.Component.NickName = "snappyHexMeshDict"
ghenv.Component.Message = 'VER 0.0.03\nJAN_26_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.snappyHexMeshDict import SnappyHexMeshDict
    #import butterfly
    #reload(butterfly)
    #reload(butterfly.foamfile)
    #reload(butterfly.snappyHexMeshDict)
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

snappyDict = SnappyHexMeshDict()

if _meshQuality_:
    raise NotImplementedError('MeshQuality is not implemented yet. It will be added soon.')

snappyDict.castellatedMesh = _castellatedMesh_
snappyDict.snap = _snap_
snappyDict.addLayers = _addLayers_

if _nCellsBetweenLevels_:
    snappyDict.nCellsBetweenLevels = str(_nCellsBetweenLevels_)

if _maxGlobalCells_:
    snappyDict.maxGlobalCells = str(_maxGlobalCells_)

if _features_:
    level= str(_level_)
    ftrs="({file "+_features_+"; level "+level+";})"
    snappyDict.features = ftrs
else:
    snappyDict.features = "()"

if additionalParameters_:
    raise NotImplementedError('additionalParameters is not implemented yet. It will be added soon.')

snappyHexMeshDict = snappyDict