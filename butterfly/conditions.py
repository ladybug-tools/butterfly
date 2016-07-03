"ABL Conditions and initialConditions class."
from foamfile import Condition
from collections import OrderedDict
import math


class ABLConditions(Condition):
    """ABL Conditions."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['Uref'] = '0'   # wind velocity
    __defaultValues['Zref'] = '10'  # reference z value - usually 10 meters
    __defaultValues['z0'] = 'uniform 1'  # roughness - default is set to 1 for urban environment
    __defaultValues['flowDir'] = '(0 1 0)'  # direction of flow
    __defaultValues['zDir'] = '(0 0 1)'  # z direction (0 0 1) always for our cases
    __defaultValues['zGround'] = 'uniform 0'  # min z value of the bounding box

    def __init__(self, values=None):
        """Init class."""
        Condition.__init__(self, name='ABLConditions', cls='dictionary',
                           location='0', defaultValues=self.__defaultValues,
                           values=values)

    @classmethod
    def fromWindTunnel(cls, BFWindTunnel):
        """Init class from BFTunnel."""
        return cls(values=BFWindTunnel.ABLConditionsDict)


class InitialConditions(Condition):
    """Initial conditions."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['flowVelocity'] = '(0 0 0)'
    __defaultValues['pressure'] = '0'
    __defaultValues['turbulentKE'] = None  # will be calculated based on input values
    __defaultValues['turbulentEpsilon'] = None  # will be calculated based on input values
    __defaultValues['#inputMode'] = 'merge'

    def __init__(self, values=None, Uref=0, Zref=10, z0=1, Cm=0.09, k=0.41):
        """Init class."""
        self.__Uref = Uref
        self.__Zref = Zref
        self.__z0 = z0
        self.__Cm = Cm
        self.__k = k
        self.calculateKEpsilon(init=True)
        Condition.__init__(self, name='initialConditions', cls='dictionary',
                           location='0', defaultValues=self.__defaultValues,
                           values=values)

    def calculateKEpsilon(self, init=False):
        """Calculate turbulentKE and turbulentEpsilon."""
        _Uabl = self.Uref * self.k / math.log((self.Zref + self.z0) / self.z0)
        epsilon = _Uabl ** 3 / self.k * (self.Zref + self.z0)
        k = _Uabl ** 2 / math.sqrt(self.Cm)

        if init:
            self.__defaultValues['turbulentKE'] = '%.3f' % k
            self.__defaultValues['turbulentEpsilon'] = '%.3f' % epsilon
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
        self.calculateKEpsilon()

    @property
    def Zref(self):
        """Input height reference for input velocity in meters."""
        return self.__Zref

    @Zref.setter
    def Zref(self, value):
        self.__Zref = float(value)
        self.calculateKEpsilon()

    @property
    def z0(self):
        """Roughness."""
        return self.__z0

    @z0.setter
    def z0(self, value):
        self.__z0 = float(value)
        self.calculateKEpsilon()

    @property
    def Cm(self):
        """Cm (default: 0.09)."""
        return self.__Cm

    @Cm.setter
    def Cm(self, value):
        self.__Cm = float(value)
        self.calculateKEpsilon()

    @property
    def k(self):
        """k (default: 0.41)."""
        return self.__k

    @k.setter
    def k(self, value):
        self.__k = float(value)
        self.calculateKEpsilon()



ic = InitialConditions(Uref=10)

print ic
