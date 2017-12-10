# coding=utf-8
"""Finite Volume Solution class."""
from foamfile import FoamFile, foam_file_from_file
from collections import OrderedDict


class SurfaceFeatureExtractDict(FoamFile):
    """surfaceFeatureExtractDict class."""

    # set default valus for this class
    __default_values = OrderedDict()

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='surfaceFeatureExtractDict', cls='dictionary',
                          location='system', default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @classmethod
    def from_stl_file(cls, file_name, extractionMethod='extractFromSurface',
                      includedAngle=150, geometricTestOnly=True, writeObj=False):
        """Generate fvSolution for a particular recipe.

        Args:
            file_name: stl file name (e.g. project.stl)
            extractionMethod: Indicate how to obtain raw features.
                extractFromFile or extractFromSurface
            includedAngle: An integer for the max angle between the faces to
                be considered as two different faces and so the edge between
                them will be considered as an edge. 0 > selects no edges and
                180 > selects all edges (default: 150).
            geometricTestOnly: A Boolean (default: True).
            writeObj: A Boolean to write features to obj format for postprocessing.
                (default: False)
        """
        _cls = cls()

        if not file_name.lower().endswith('.stl'):
            file_name = file_name + '.stl'

        _values = {
            file_name: {
                'extractionMethod': extractionMethod,
                'extractFromSurfaceCoeffs': {
                    'includedAngle': str(includedAngle),
                    'geometricTestOnly': _cls.convert_bool_value(geometricTestOnly)
                },
                'writeObj': _cls.convert_bool_value(writeObj)
            }
        }

        # update values based on the recipe.
        _cls.update_values(_values, mute=True)
        return _cls
