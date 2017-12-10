# coding=utf-8
"""Roughness values."""
import copy


class Z0(object):
    """Typical roughness values based on landscape."""

    __roughnessDict = {
        0: '0.0002', 'sea': '0.0002',
        1: '0.005', 'smooth': '0.005',
        2: '0.03', 'open': '0.03',
        3: '0.10', 'roughlyOpen': '0.10',
        4: '0.25', 'rough': '0.25',
        5: '0.5', 'veryRough': '0.5',
        6: '1.0', 'closed': '1.0',
        7: '2.0', 'chaotic': '2.0'
    }

    def __init__(self):
        pass

    @property
    def sea(self):
        """Roughness value for open sea or lake."""
        return self.__roughnessDict['sea']

    @property
    def smooth(self):
        """Roughness value for featureless land geometries."""
        return self.__roughnessDict['smooth']

    @property
    def open(self):
        """Roughness value for country with low vegetation."""
        return self.__roughnessDict['open']

    @property
    def roughly_open(self):
        """Roughness value for cultivated area with regular cover of low crops."""
        return self.__roughnessDict['roughlyOpen']

    @property
    def rough(self):
        """Roughness value for new landscape with scattred obstacles."""
        return self.__roughnessDict['rough']

    @property
    def very_rough(self):
        """Roughness value for 'old' cultivated landscape."""
        return self.__roughnessDict['veryRough']

    @property
    def closed(self):
        """Roughness value for landscape totally and quite regularly covered."""
        return self.__roughnessDict['closed']

    @property
    def chaotic(self):
        """Roughness value for center of large towns."""
        return self.__roughnessDict['chaotic']

    def __getitem__(self, index):
        """Get roughness value by index."""
        return self.__roughnessDict[index]

    def duplicate(self):
        """Return a copy of this object."""
        return copy.deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Roughness library."""
        return 'Z0 (Roughness) dict.'
