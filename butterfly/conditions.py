# coding=utf-8
"""ABL Conditions and initial_conditions class."""
from .foamfile import Condition, foam_file_from_file
from collections import OrderedDict
import math


class ABLConditions(Condition):
    """ABL Conditions."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['Uref'] = '0'   # wind velocity
    __default_values['Zref'] = '10'  # reference z value - usually 10 meters
    # roughness - default is set to 1 for urban environment
    __default_values['z0'] = 'uniform 1'
    __default_values['flowDir'] = '(0 1 0)'  # direction of flow
    __default_values['zDir'] = '(0 0 1)'  # z direction (0 0 1) always for our cases
    __default_values['zGround'] = 'uniform 0'  # min z value of the bounding box
    __default_values['value'] = '$internalField'

    def __init__(self, values=None):
        """Init class."""
        super(ABLConditions, self).__init__(
            name='ABLConditions', cls='dictionary', location='0',
            default_values=self.__default_values, values=values
        )

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @classmethod
    def from_input_values(cls, flow_speed, z0, flow_dir, z_ground):
        """Get ABLCondition."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(flow_speed)
        _ABLCDict['z0'] = 'uniform {}'.format(z0)
        _ABLCDict['flowDir'] = flow_dir if isinstance(flow_dir, str) \
            else '({} {} {})'.format(*flow_dir)

        _ABLCDict['zGround'] = 'uniform {}'.format(z_ground)
        return cls(_ABLCDict)

    @classmethod
    def from_wind_tunnel(cls, wind_tunnel):
        """Init class from wind tunnel."""
        return cls(values=wind_tunnel.ABLConditionsDict)

    @property
    def flow_dir(self):
        """Get flow dir as tuple (x, y, z)."""
        return eval(self.values['flowDir'])

    @property
    def flow_speed(self):
        """Get flow speed as a float."""
        return float(self.values['Uref'])


class InitialConditions(Condition):
    """Initial conditions."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['flowVelocity'] = '(0 0 0)'
    __default_values['pressure'] = '0'
    __default_values['turbulentKE'] = None  # will be calculated based on input values
    __default_values['turbulentEpsilon'] = None  # will be calculated based on inp values
    __default_values['#inputMode'] = 'merge'

    def __init__(self, values=None, Uref=0, Zref=10, z0=1, cm=0.09, k=0.41):
        """Init class.

        Args:
            Uref: Reference wind velocity in m/s.
            Zref: Reference height for wind velocity. Normally 10 m.
            z0: Roughness (default: 1).
        """
        self.__Uref = float(Uref)
        self.__Zref = float(Zref)
        self.__z0 = float(z0)
        self.__cm = cm
        self.__k = k
        self.calculate_k_epsilon(init=True)
        super(InitialConditions, self).__init__(
            name='initial_conditions', cls='dictionary', location='0',
            default_values=self.__default_values, values=values
        )

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    def calculate_k_epsilon(self, init=False):
        """Calculate turbulentKE and turbulentEpsilon.

        Args:
            init: True if the method is called when the class is initiated
                (default: False).
        """
        _Uabl = self.Uref * self.k / math.log((self.Zref + self.z0) / self.z0)
        epsilon = _Uabl ** 3 / (self.k * (self.Zref + self.z0))
        k = _Uabl ** 2 / math.sqrt(self.cm)

        if init:
            self.__default_values['turbulentKE'] = '%.5f' % k
            self.__default_values['turbulentEpsilon'] = '%.5f' % epsilon
        else:
            self.values['turbulentKE'] = str(k)
            self.values['turbulentEpsilon'] = str(epsilon)

    @property
    def Uref(self):
        """Input velocity in m/s."""
        return self.__Uref

    @Uref.setter
    def Uref(self, value):
        """Input velocity in m/s."""
        self.__Uref = float(value)
        self.calculate_k_epsilon()

    @property
    def Zref(self):
        """Input height reference for input velocity in meters."""
        return self.__Zref

    @Zref.setter
    def Zref(self, value):
        self.__Zref = float(value)
        self.calculate_k_epsilon()

    @property
    def z0(self):
        """Roughness."""
        return self.__z0

    @z0.setter
    def z0(self, value):
        self.__z0 = float(value)
        self.calculate_k_epsilon()

    @property
    def cm(self):
        """cm.

        default: 0.09
        """
        return self.__cm

    @cm.setter
    def cm(self, value):
        self.__cm = float(value)
        self.calculate_k_epsilon()

    @property
    def k(self):
        """k.

        default: 0.41
        """
        return self.__k

    @k.setter
    def k(self, value):
        self.__k = float(value)
        self.calculate_k_epsilon()
