"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from fields import AtmBoundaryLayerInletVelocity, AtmBoundaryLayerInletK, \
    AtmBoundaryLayerInletEpsilon, Calculated, EpsilonWallFunction, FixedValue, \
    InletOutlet, KqRWallFunction, NutkWallFunction, NutkAtmRoughWallFunction, \
    Slip, ZeroGradient


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
        self.refLevels = (0, 0) if not refLevels else tuple(int(v) for v in refLevels)
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


class BoundingBoxBoundaryCondition(BoundaryCondition):
    """Bounding box boundary condition for bounding box surface.

    It returns a boundary condition of ZeroGradient for all the inputs.
    """
    def __init__(self, refLevels=None):
        """Init bounday condition."""
        u = ZeroGradient()
        p = ZeroGradient()
        k = ZeroGradient()
        epsilon = ZeroGradient()
        nut = ZeroGradient()
        refLevels = None
        temperature = None
        BoundaryCondition.__init__(self, 'wall', refLevels, temperature, u, p,
                                   k, epsilon, nut)


class IndoorWallBoundaryCondition(BoundaryCondition):
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
        epsilon = EpsilonWallFunction(0.01) \
            if not epsilon else epsilon
        nut = NutkWallFunction(0.01) \
            if not nut else nut

        BoundaryCondition.__init__(self, 'wall', refLevels, temperature, u, p,
                                   k, epsilon, nut)


class FixedInletBoundaryCondition(BoundaryCondition):
    """Inlet boundary condition base class.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: Air velocity as fixed value (x, y, z).
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


class FixedOutletBoundaryCondition(BoundaryCondition):
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


class WindTunnelWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition for wall surfaces inside wind tunnel.

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
        k = KqRWallFunction('$internalField') if not k else k
        epsilon = EpsilonWallFunction('$internalField') \
            if not epsilon else epsilon
        nut = NutkWallFunction('0.0') \
            if not nut else nut

        BoundaryCondition.__init__(self, 'wall', refLevels, temperature, u, p,
                                   k, epsilon, nut)


class WindTunnelGroundBoundaryCondition(BoundaryCondition):
    """Wind tunnel ground boundary condition.

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
    def __init__(self, ablConditions, refLevels=None, temperature=None,
                 u=None, p=None, k=None, epsilon=None):
        """Init bounday condition."""
        u = FixedValue('(0 0 0)') if not u else u
        p = ZeroGradient() if not p else p
        k = ZeroGradient() if not k else k
        epsilon = ZeroGradient() if not epsilon else epsilon
        nut = NutkAtmRoughWallFunction.fromABLConditions(ablConditions,
                                                         'uniform 0')

        BoundaryCondition.__init__(self, 'wall', refLevels, temperature, u, p,
                                   k, epsilon, nut)


class WindTunnelInletBoundaryCondition(BoundaryCondition):
    """Wind tunnel atmBoundaryLayerInletVelocity boundary condition.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this surface.
        temperature: Optional input for Temperature
        u: OpenFOAM value for u.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """
    def __init__(self, ablConditions, refLevels=None, temperature=None, p=None,
                 nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        u = AtmBoundaryLayerInletVelocity.fromABLConditions(ablConditions)
        k = AtmBoundaryLayerInletK.fromABLConditions(ablConditions)
        epsilon = AtmBoundaryLayerInletEpsilon.fromABLConditions(ablConditions)
        p = ZeroGradient() if not p else p
        nut = Calculated(0) if not nut else nut

        BoundaryCondition.__init__(self, 'patch', refLevels, temperature, u, p,
                                   k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.u.Uref, self.refLevels)


class WindTunnelOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for wind tunnel.

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
        u = InletOutlet('uniform (0 0 0)', '$internalField') if not u else u
        p = FixedValue('$pressure') if not p else p
        k = InletOutlet('uniform $turbulentKE', '$internalField') \
            if not k else k
        epsilon = InletOutlet('uniform $turbulentEpsilon', '$internalField') \
            if not epsilon else epsilon
        nut = Calculated(0) if not nut else nut

        BoundaryCondition.__init__(self, 'patch', refLevels, temperature, u, p,
                                   k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)


class WindTunnelTopAndSidesBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for top and sides of wind tunnel.

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
        u = Slip() if not u else u
        p = Slip() if not p else p
        k = Slip() if not k else k
        epsilon = Slip() if not epsilon else epsilon
        nut = Calculated(0)

        BoundaryCondition.__init__(self, 'patch', refLevels, temperature, u, p,
                                   k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.refLevels)


if __name__ == '__main__':
    from conditions import ABLConditions
    abc = ABLConditions()
    print WindTunnelInletBoundaryCondition(abc)
    print
    print WindTunnelGroundBoundaryCondition(abc)
