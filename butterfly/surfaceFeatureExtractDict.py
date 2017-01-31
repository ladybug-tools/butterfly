# coding=utf-8
"""Finite Volume Solution class."""
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class SurfaceFeatureExtractDict(FoamFile):
    """surfaceFeatureExtractDict class."""

    # set default valus for this class
    __defaultValues = OrderedDict()

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='surfaceFeatureExtractDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    @classmethod
    def fromStlFile(cls, fileName, extractionMethod='extractFromSurface',
                    includedAngle=150, geometricTestOnly=True, writeObj=False):
        """Generate fvSolution for a particular recipe.

        Args:
            fileName: stl file name (e.g. project.stl)
            extractionMethod: Indicate how to obtain raw features.
                extractFromFile or extractFromSurface
            includedAngle: An integer for the max angle between the faces to
                be considered as two different faces and so the edge between
                them will be considered as an edge. 0 > selects no edges and
                180 > selects all edges (default: 150).
            writeObj: A Boolean to write features to obj format for postprocessing.
                (default: True)
        """
        _cls = cls()

        if not fileName.lower().endswith('.stl'):
            fileName = fileName + '.stl'

        _values = {
            fileName: {
                'extractionMethod': extractionMethod,
                'extractFromSurfaceCoeffs': {
                    'includedAngle': str(includedAngle),
                    'geometricTestOnly': _cls.convertBoolValue(geometricTestOnly)
                },
                'writeObj': _cls.convertBoolValue(writeObj)
            }
        }

        # update values based on the recipe.
        _cls.updateValues(_values, mute=True)
        return _cls
