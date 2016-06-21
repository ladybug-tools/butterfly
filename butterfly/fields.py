"""OpenFOAM field values."""
from collections import OrderedDict

class OpenFOAMValue(object):
    """OpenFOAM field values base class."""
    def __init__(self):
        self.type = self.__class__.__name__[:1].lower() + \
                    self.__class__.__name__[1:]

    @property
    def valueDict(self):
        """Get fields as a dictionary."""
        return {'type': self.type}

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        return "\n".join(("{}        {};").format(key, value)
                         for key, value in self.valueDict.iteritems())


class ZeroGradient(OpenFOAMValue):
    pass


class Calculated(OpenFOAMValue):
    pass


class FixedValue(OpenFOAMValue):
    """OpenFOAM fixed value."""
    def __init__(self, value):
        OpenFOAMValue.__init__(self)
        self.value = 'uniform {}'.format(str(value))

    @property
    def valueDict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['value'] = self.value
        return _d


class WallFunction(FixedValue):
    pass


class KqRWallFunction(WallFunction):
    pass

class EpsilonWallFunction(WallFunction):
    def __init__(self, value, Cmu, kappa, E):
        WallFunction.__init__(self, value)
        self.cmu = Cmu
        self.kappa = kappa
        self.e = E

    @property
    def valueDict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = str(self.type)
        _d['value'] = str(self.value)
        _d['Cmu'] = str(self.cmu)
        _d['kappa'] = str(self.kappa)
        _d['E'] = str(self.e)
        return _d

class NutkWallFunction(EpsilonWallFunction):
    pass
