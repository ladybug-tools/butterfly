# assign inputs
_meshQuality_, _castellatedMesh_, _snap_, _addLayers_, _nCellsBetweenLevels_, _maxGlobalCells_, _surfaceFeatureLevel_, _expansionRatio_, _finalLayerThickness_, _minThickness_, _nLayerIter_, additionalParameters_ = IN
snappyHexMeshDict = None

try:
    from butterfly.solution import SolutionParameter
    from butterfly.parser import CppDictParser
    from butterfly.utilities import updateDict
except ImportError as e:
    msg = '\nFailed to import butterfly. Did you install butterfly on your machine?' + \
            '\nYou can download butterfly from package manager.' + \
            '\nOpen an issue on github if you think this is a bug:' + \
            ' https://github.com/ladybug-analysis-tools/butterfly/issues'
        
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


# assign outputs to OUT
OUT = (snappyHexMeshDict,)