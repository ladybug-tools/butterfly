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

    def __init__(self, inlet_value, value):
        """Init class."""
        Field.__init__(self)
        self.inlet_value = inlet_value
        self.value = value

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['inlet_value'] = self.inlet_value
        _d['value'] = self.value
        return _d


class OutletInlet(Field):
    """OpenFOAM OutletInlet value.

    http://www.cfd-online.com/Forums/openfoam-solving/60337-questions-about
    -inletoutlet-outletinlet-boundary-conditions.html
    """

    def __init__(self, outlet_value, value):
        """Init class."""
        Field.__init__(self)
        self.outlet_value = outlet_value
        self.value = value

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['outlet_value'] = self.outlet_value
        _d['value'] = self.value
        return _d


class AtmBoundary(Field):
    """OpenFOAM AtmBoundaryLayerInletVelocity.

    Attributes:
        uref: Flow velocity as a float number.
        zref: Reference z value for flow velocity as a float number.
        z0: Roughness (e.g. uniform 1).
        flow_dir: Velocity vector as a tuple.
        zDir: Z direction (default:(0 0 1)).
        z_ground: Min z value of the bounding box (default: 0).
        from_values: True.
    """

    def __init__(self, uref, zref, z0, flow_dir, zDir='(0 0 1)', z_ground=0,
                 from_values=True):
        """Create from values.

        Args:
            uref: Flow velocity as a float number.
            zref: Reference z value for flow velocity as a float number.
            z0: Roughness (e.g. uniform 1).
            flow_dir: Velocity vector as a tuple.
            zDir: Z direction (default:(0 0 1)).
            z_ground: Min z value of the bounding box (default: 0).
        """
        self.from_values = from_values
        Field.__init__(self)
        self.uref = uref
        self.zref = zref
        self.z0 = z0
        self.flow_dir = flow_dir
        self.zDir = zDir
        self.z_ground = z_ground

    @classmethod
    def from_ABLConditions(cls, ABLConditions, value=None):
        """Init class from a condition file."""
        _cls = cls(ABLConditions.values['Uref'], ABLConditions.values['zref'],
                   ABLConditions.values['z0'], ABLConditions.values['flow_dir'],
                   ABLConditions.values['zDir'], ABLConditions.values['z_ground'],
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
            _d['Uref'] = self.uref
            _d['zref'] = self.zref
            _d['z0'] = self.z0
            _d['flow_dir'] = self.flow_dir
            _d['zDir'] = self.zDir
            _d['z_ground'] = self.z_ground

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

    def __init__(self, value, is_uniform=True, prt=None):
        """Init class."""
        FixedValue.__init__(self, value, is_uniform)
        self.prt = str(prt) if prt else '0.85'

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['value'] = self.value
        _d['Prt'] = self.prt
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

    def __init__(self, volumetric_flow_rate, value, is_uniform=True):
        """Init class."""
        FixedValue.__init__(self, value, is_uniform)
        self.volumetric_flow_rate = volumetric_flow_rate

    @property
    def value_dict(self):
        """Get fields as a dictionary."""
        _d = OrderedDict()
        _d['type'] = self.type
        _d['volumetric_flow_rate'] = self.volumetric_flow_rate
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
        self.e = E

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
        if self.e:
            _d['E'] = str(self.e)

        return _d


class NutkWallFunction(EpsilonWallFunction):
    """NutkWallFunction."""

    pass
