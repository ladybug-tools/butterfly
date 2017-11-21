# coding=utf-8
"""OpenFOAM field values."""
from collections import OrderedDict
from copy import deepcopy


class Field(object):
    """OpenFOAM field values base class."""

    def __init__(self):
        """Init class."""
        self.type = self.__class__.__name__[:1].lower() + \
            self.__class__.__name__[1:]
        self.__values = {}
        self.__values['type'] = self.type

    @classmethod
    def from_dict(cls, d):
        """Create a field from a dictionary."""
        _cls = cls()
        assert isinstance(d, (OrderedDict, dict)), \
            ValueError('Input should be a dictionary not {}'.format(type(d)))
        assert 'type' in d, ValueError('"type" is missing from {}'.format(d))
        _cls.__values = d
        return _cls

    @classmethod
    def from_string(cls, st):
        """Create a field from a string."""
        d = {s.split()[0]: ' '.join(s.split()[1:])
             for s in st.replace('{', '').replace('}', '').split(';')
             if s.strip()}
        return cls.from_dict(d)

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        return self.__values

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Representation."""
        return "\n".join(("{}        {};").format(key, value)
                         for key, value in self.value_dict.iteritems())


class ZeroGradient(Field):
    """ZeroGradient boundary condition."""

    pass


class Slip(Field):
    """Slip boundary condition."""

    pass


class Empty(Field):
    """Empty boundary condition."""

    pass


class Calculated(Field):
    """OpenFOAM calculated value.

    Args:
        value: value.
        is_unifrom: A boolean that indicates if the values is uniform.
    """

    def __init__(self, value=None, is_unifrom=True):
        """Init Calculated class."""
        Field.__init__(self)
        if value:
            self.value = 'uniform {}'.format(str(value)) if is_unifrom else str(value)
        else:
            self.value = None

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        if self.value:
            _d['type'] = self.type
            _d['value'] = self.value
        else:
            _d['type'] = self.type

        return _d


class InletOutlet(Field):
    """OpenFOAM InletOutlet value.

    http://www.cfd-online.com/Forums/openfoam-solving/60337-questions-about
    -inletoutlet-outletinlet-boundary-conditions.html
    """

    def __init__(self, inletValue, value):
        """Init class."""
        Field.__init__(self)
        self.inletValue = inletValue
        self.value = value

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['inletValue'] = self.inletValue
        _d['value'] = self.value
        return _d


class OutletInlet(Field):
    """OpenFOAM OutletInlet value.

    http://www.cfd-online.com/Forums/openfoam-solving/60337-questions-about
    -inletoutlet-outletinlet-boundary-conditions.html
    """

    def __init__(self, outletValue, value):
        """Init class."""
        Field.__init__(self)
        self.outletValue = outletValue
        self.value = value

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['outletValue'] = self.outletValue
        _d['value'] = self.value
        return _d


class AtmBoundary(Field):
    """OpenFOAM AtmBoundaryLayerInletVelocity.

    Attributes:
        uref: Flow velocity as a float number.
        Zref: Reference z value for flow velocity as a float number.
        z0: Roughness (e.g. uniform 1).
        flowDir: Velocity vector as a tuple.
        zDir: Z direction (default:(0 0 1)).
        zGround: Min z value of the bounding box (default: 0).
        from_values: True.
    """

    def __init__(self, Uref, Zref, z0, flowDir, zDir='(0 0 1)', zGround=0,
                 from_values=True):
        """Create from values.

        Args:
            Uref: Flow velocity as a float number.
            Zref: Reference z value for flow velocity as a float number.
            z0: Roughness (e.g. uniform 1).
            flowDir: Velocity vector as a tuple.
            zDir: Z direction (default:(0 0 1)).
            zGround: Min z value of the bounding box (default: 0).
        """
        self.from_values = from_values
        Field.__init__(self)
        self.Uref = Uref
        self.Zref = Zref
        self.z0 = z0
        self.flowDir = flowDir
        self.zDir = zDir
        self.zGround = zGround

    @classmethod
    def from_ABLConditions(cls, ABLConditions, value=None):
        """Init class from a condition file."""
        _cls = cls(ABLConditions.values['Uref'], ABLConditions.values['Zref'],
                   ABLConditions.values['z0'], ABLConditions.values['flowDir'],
                   ABLConditions.values['zDir'], ABLConditions.values['zGround'],
                   from_values=False)
        _cls.value = value
        _cls.ABLConditions = ABLConditions
        return _cls

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        if not self.from_values:
            _d['#include'] = '"{}"'.format(self.ABLConditions.__class__.__name__)
            if self.value:
                _d['value'] = str(self.value)

        else:
            _d['Uref'] = self.Uref
            _d['Zref'] = self.Zref
            _d['z0'] = self.z0
            _d['flowDir'] = self.flowDir
            _d['zDir'] = self.zDir
            _d['zGround'] = self.zGround

        return _d


class AtmBoundaryLayerInletVelocity(AtmBoundary):
    """AtmBoundaryLayerInletVelocity."""

    pass


class AtmBoundaryLayerInletK(AtmBoundary):
    """AtmBoundaryLayerInletK."""

    pass


class AtmBoundaryLayerInletEpsilon(AtmBoundary):
    """AtmBoundaryLayerInletEpsilon."""

    pass


class NutkAtmRoughWallFunction(AtmBoundary):
    """NutkAtmRoughWallFunction."""

    pass


class FixedValue(Field):
    """OpenFOAM fixed value.

    Args:
        value: value.
        is_unifrom: A boolean that indicates if the values is uniform.
    """

    def __init__(self, value, is_unifrom=True):
        """Init the class."""
        Field.__init__(self)
        self.value = 'uniform {}'.format(str(value)) if is_unifrom else str(value)

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['value'] = self.value
        return _d


class PressureInletOutletVelocity(FixedValue):
    """PressureInletOutletVelocity."""

    pass


class AlphatJayatillekeWallFunction(FixedValue):
    """alphatJayatillekeWallFunction."""

    def __init__(self, value, is_uniform=True, Prt=None):
        """Init class."""
        FixedValue.__init__(self, value, is_uniform)
        self.Prt = str(Prt) if Prt else '0.85'

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['value'] = self.value
        _d['Prt'] = self.Prt
        return _d


class FixedFluxPressure(FixedValue):
    """FixedFluxPressure."""

    def __init__(self, value, is_uniform=True, rho=None):
        """Init class."""
        FixedValue.__init__(self, value, is_uniform)
        self.rho = rho if rho else 'rhok'

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['value'] = self.value
        _d['rho'] = self.rho
        return _d


class FlowRateInletVelocity(FixedValue):
    """FlowRateInletVelocity."""

    def __init__(self, volumetricFlowRate, value, is_uniform=True):
        """Init class."""
        FixedValue.__init__(self, value, is_uniform)
        self.volumetricFlowRate = volumetricFlowRate

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['volumetricFlowRate'] = self.volumetricFlowRate
        _d['value'] = self.value
        return _d


class WallFunction(FixedValue):
    """WallFunction."""

    pass


class KqRWallFunction(WallFunction):
    """KqRWallFunction."""

    pass


class EpsilonWallFunction(WallFunction):
    """EpsilonWallFunction.

    Args:
        value:
        cmu: (default: None)
        kappa: (default: None)
        E: (default: None)
    """

    # default values in OpenFOAM cmu=0.09, kappa=0.41, E=9.8
    def __init__(self, value, cmu=None, kappa=None, E=None, is_unifrom=True):
        """Init EpsilonWallFunction."""
        WallFunction.__init__(self, value, is_unifrom)
        self.cmu = cmu
        self.kappa = kappa
        self.E = E

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = str(self.type)
        _d['value'] = str(self.value)
        if self.cmu:
            _d['cmu'] = str(self.cmu)
        if self.kappa:
            _d['kappa'] = str(self.kappa)
        if self.E:
            _d['E'] = str(self.E)

        return _d


class NutkWallFunction(EpsilonWallFunction):
    """NutkWallFunction."""

    pass
