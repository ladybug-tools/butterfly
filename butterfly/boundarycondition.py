"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from fields import Calculated, ZeroGradient, FixedValue, EpsilonWallFunction, \
    KqRWallFunction, NutkWallFunction

class BoundaryCondition(object):
    """Boundary condition base class.

    Attributes:
        bcType: Boundary condition type. e.g.(patch, wall)
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: OpenFOAM value for u.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """
    def __init__(self, bcType='patch', refLevels=None, temperature=None,
                 u=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        self.type = bcType
        self.temperature = temperature
        self.refLevels = (0, 0) if not refLevels else refLevels
        # set default values
        self.u = ZeroGradient() if not u else u
        self.p = ZeroGradient() if not p else p
        self.k = ZeroGradient() if not k else k
        self.epsilon = ZeroGradient() if not epsilon else epsilon
        self.nut = ZeroGradient() if not nut else nut

    def duplicate(self):
        """Duplicate Boundary Condition."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}; refLevels {}".format(self.__class__.__name__,
                                             self.type, self.refLevels)


class WallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition base class.

    Attributes:
        temperature: Optional input for Temperature
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: OpenFOAM value for u.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """
    def __init__(self, refLevels=None, temperature=None,
                 u=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        u = FixedValue('(0 0 0)') if not u else u
        p = ZeroGradient() if not p else p
        k = KqRWallFunction('0.1') if not k else k
        epsilon = EpsilonWallFunction(0.01, Cmu=0.09, kappa=0.41, E=9.8) \
            if not epsilon else epsilon
        nut = NutkWallFunction(0.01, Cmu=0.09, kappa=0.41, E=9.8) \
            if not nut else nut

        BoundaryCondition.__init__(self, 'wall', refLevels, temperature, u, p,
                                   k, epsilon, nut)


class InletBoundaryCondition(BoundaryCondition):
    """Inlet boundary condition base class.

    Attributes:
        velocityVector: Velocity vector as a tupel (default: (0, 0, 0))
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: OpenFOAM value for u.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """
    def __init__(self, refLevels=None, temperature=None,
                 u=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        u = FixedValue('(0 0 0)') if not u else u
        p = FixedValue('0') if not p else p
        k = FixedValue('0.1') if not k else k
        epsilon = FixedValue('0.01') if not epsilon else epsilon
        nut = Calculated()

        BoundaryCondition.__init__(self, 'patch', refLevels, temperature, u, p,
                                   k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.u, self.refLevels)


class OutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition base class.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: OpenFOAM value for u.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """
    def __init__(self, refLevels=None, temperature=None,
                 u=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        u = ZeroGradient() if not u else u
        p = ZeroGradient() if not p else p
        k = ZeroGradient() if not k else k
        epsilon = ZeroGradient() if not epsilon else epsilon
        nut = Calculated()

        BoundaryCondition.__init__(self, 'patch', refLevels, temperature, u, p,
                                   k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)
