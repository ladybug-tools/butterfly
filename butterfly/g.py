# coding=utf-8
"""g[ravity] class."""
from foamfile import FoamFile, foam_file_from_file
from collections import OrderedDict


class G(FoamFile):
    """G (gravity) class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['dimensions'] = '[0 1 -2 0 0 0 0]'
    __default_values['#include'] = None
    __default_values['value'] = '(0 0 -9.81)'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='g',
                          cls='uniformDimensionedVectorField',
                          location='constant',
                          default_values=self.__default_values,
                          values=values)

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @property
    def dimensions(self):
        return self.values['dimensions']

    @property
    def value(self):
        """Gravity vector."""
        return eval(self.values['value'].replace(' ', ','))

    @value.setter
    def value(self, vec):
        """Set gravity vector."""
        assert len(vec) == 3, \
            ValueError('Gravity vector must be a tuple with 3 values.')
        self.values['value'] = '({})'.format(' '.join((str(v) for v in vec)))
