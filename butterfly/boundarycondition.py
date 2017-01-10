# coding=utf-8
"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from fields import AtmBoundaryLayerInletVelocity, AtmBoundaryLayerInletK, \
    AtmBoundaryLayerInletEpsilon, Calculated, EpsilonWallFunction, FixedValue, \
    InletOutlet, KqRWallFunction, NutkWallFunction, NutkAtmRoughWallFunction, \
    Slip, ZeroGradient, AlphatJayatillekeWallFunction, FixedFluxPressure, Empty


class BoundaryCondition(object):
    """Boundary condition base class.

    Attributes:
        bcType: Boundary condition type. e.g.(patch, wall)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for temperature in Kelvin (300)
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, bcType='patch', refLevels=None, T=None, U=None, p=None,
                 k=None, epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        self.type = bcType
        self.T = T or ZeroGradient()
        self.refLevels = (1, 1) if not refLevels else tuple(int(v) for v in refLevels)
        # set default values
        self.U = U or ZeroGradient()
        self.p = p or ZeroGradient()
        self.k = k or ZeroGradient()
        self.epsilon = epsilon or ZeroGradient()
        self.nut = nut or ZeroGradient()
        self.alphat = alphat or ZeroGradient()
        self.p_rgh = p_rgh or ZeroGradient()

    def isBoundaryCondition(self):
        """Return True for boundary conditions."""
        return True

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
    """Bounding box boundary condition for bounding box geometry.

    It returns a boundary condition of ZeroGradient for all the inputs.
    """

    def __init__(self, refLevels=None):
        """Init bounday condition."""
        U = ZeroGradient()
        p = ZeroGradient()
        k = ZeroGradient()
        epsilon = ZeroGradient()
        nut = ZeroGradient()
        refLevels = None
        T = ZeroGradient()
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()
        super(BoundingBoxBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class EmptyBoundaryCondition(BoundaryCondition):
    """Empty boundary condition.

    It returns a boundary condition of Empty for all the inputs.
    """

    def __init__(self, refLevels=None):
        """Init bounday condition."""
        U = Empty()
        p = Empty()
        k = Empty()
        epsilon = Empty()
        nut = Empty()
        refLevels = None
        T = Empty()
        alphat = Empty()
        p_rgh = Empty()
        super(EmptyBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class IndoorWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition base class.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('0.1')
        epsilon = epsilon or EpsilonWallFunction(0.01)
        nut = nut or NutkWallFunction(0.01)
        T = T or ZeroGradient()
        alphat = alphat or AlphatJayatillekeWallFunction(
            value='0', isUniform=True, Prt='0.85')

        p_rgh = p_rgh or FixedFluxPressure(value='0', isUniform=True, rho='rhok')

        BoundaryCondition.__init__(self, 'wall', refLevels, T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)


class FixedInletBoundaryCondition(BoundaryCondition):
    """Inlet boundary condition base class.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: Air velocity as fixed value (x, y, z).
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or FixedValue('0.1')
        epsilon = epsilon or FixedValue('0.01')
        nut = Calculated('0')
        T = T if T else None
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()

        BoundaryCondition.__init__(self, 'patch', refLevels, T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.U, self.refLevels)


class FixedOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition base class.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or ZeroGradient()
        p = p or FixedValue('0')
        k = k or ZeroGradient()
        epsilon = epsilon or ZeroGradient()
        nut = Calculated('0')
        T = T or ZeroGradient()
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()

        super(FixedOutletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)


class WindTunnelWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition for wall geometrys inside wind tunnel.

    Attributes:
        T: Optional input for Temperature.
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('$internalField', isUnifrom=False)
        epsilon = epsilon or EpsilonWallFunction('$internalField', isUnifrom=False)
        nut = nut or NutkWallFunction('0.0')
        T = T or ZeroGradient()
        super(WindTunnelWallBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut
        )


class WindTunnelGroundBoundaryCondition(BoundaryCondition):
    """Wind tunnel ground boundary condition.

    Attributes:
        T: Optional input for Temperature.
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ablConditions, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or ZeroGradient()
        epsilon = epsilon or ZeroGradient()
        nut = NutkAtmRoughWallFunction.fromABLConditions(ablConditions,
                                                         'uniform 0')
        T = T or ZeroGradient()

        super(WindTunnelGroundBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut
        )


class WindTunnelInletBoundaryCondition(BoundaryCondition):
    """Wind tunnel atmBoundaryLayerInletVelocity boundary condition.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ablConditions, refLevels=None, T=None, p=None,
                 nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = AtmBoundaryLayerInletVelocity.fromABLConditions(ablConditions)
        k = AtmBoundaryLayerInletK.fromABLConditions(ablConditions)
        epsilon = AtmBoundaryLayerInletEpsilon.fromABLConditions(ablConditions)
        p = p or ZeroGradient()
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelInletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.U.Uref, self.refLevels)


class WindTunnelOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or InletOutlet('uniform (0 0 0)', '$internalField')
        p = p or FixedValue('$pressure')
        k = k or InletOutlet('uniform $turbulentKE', '$internalField')
        epsilon = epsilon or InletOutlet('uniform $turbulentEpsilon', '$internalField')
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelOutletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)


class WindTunnelTopAndSidesBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for top and sides of wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or Slip()
        p = p or Slip()
        k = k or Slip()
        epsilon = epsilon or Slip()
        nut = Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelTopAndSidesBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.refLevels)


if __name__ == '__main__':
    from conditions import ABLConditions
    abc = ABLConditions()
    print WindTunnelWallBoundaryCondition()
    print WindTunnelInletBoundaryCondition(abc)
    print
    print WindTunnelGroundBoundaryCondition(abc)
