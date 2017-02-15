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
        _surfaceFeatureLevel_: An integer for the extract features refinement. Default is None which
            means implicit meshing feature will be used.
        _expansionRatio_: Layers expansion ration (default: 1.1)
        _finalLayerThickness_: Thickness of final layer (default: 0.7)
        _minThickness_: Minimum thickness for layers (default: 0.1).
        _nLayerIter_: Overall max number of layer addition iterations. The mesher
            will exit if it reaches this number of iterations; possibly with an
            illegal mesh (default: 50).
        additionalParameters_: Additional parameters as a valid c++ dictionary. Additional values
            will overwrite the values from the other inputs above.
    Returns:
        snappyHexMeshDict: Butterfly snappyHexMeshDict.
"""

ghenv.Component.Name = "Butterfly_snappyHexMeshDict"
ghenv.Component.NickName = "snappyHexMeshDict"
ghenv.Component.Message = 'VER 0.0.03\nFEB_14_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from butterfly.solution import SolutionParameter
    from butterfly.parser import CppDictParser
    from butterfly.utilities import updateDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download the installer file from github: ' + \
            'https://github.com/mostaphaRoudsari/Butterfly/tree/master/plugin/grasshopper/samplefiles' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/mostaphaRoudsari/Butterfly/issues'
        
    raise ImportError('{}\n{}'.format(msg, e))

if _meshQuality_:
    raise NotImplementedError('MeshQuality is not implemented yet. It will be added soon.')

values = {'castellatedMesh': str(_castellatedMesh_).lower(),
          'snap': str(_snap_).lower(), 'addLayers': str(_addLayers_).lower(),
          'castellatedMeshControls': {
            'nCellsBetweenLevels': str(_nCellsBetweenLevels_),
            'maxGlobalCells': str(_maxGlobalCells_)
            },
           'addLayersControls': {
                'expansionRatio': str(_expansionRatio_),
                'finalLayerThickness': str(_finalLayerThickness_),
                'minThickness': str(_minThickness_),
                'nLayerIter': str(_nLayerIter_)}
          }

if _surfaceFeatureLevel_ is not None:
    values['snapControls'] = {'extractFeaturesRefineLevel': str(_surfaceFeatureLevel_)}

if additionalParameters_:
    try:
        addedValues = CppDictParser(additionalParameters_).values
    except Exception as e:
        raise ValueError("Failed to load additionalParameters_:\n%s" % str(e))
    else:
        values = updateDict(values, addedValues)

snappyHexMeshDict = SolutionParameter('snappyHexMeshDict', values)
