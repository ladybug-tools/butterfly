# coding=utf-8
"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from fields import AtmBoundaryLayerInletVelocity, AtmBoundaryLayerInletK, \
    AtmBoundaryLayerInletEpsilon, Calculated, EpsilonWallFunction, FixedValue, \
    InletOutlet, KqRWallFunction, NutkWallFunction, NutkAtmRoughWallFunction, \
    Slip, ZeroGradient, AlphatJayatillekeWallFunction, FixedFluxPressure


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
        self.T = ZeroGradient() if not T else T
        self.refLevels = (0, 0) if not refLevels else tuple(int(v) for v in refLevels)
        # set default values
        self.U = ZeroGradient() if not U else U
        self.p = ZeroGradient() if not p else p
        self.k = ZeroGradient() if not k else k
        self.epsilon = ZeroGradient() if not epsilon else epsilon
        self.nut = ZeroGradient() if not nut else nut
        self.alphat = ZeroGradient() if not alphat else alphat
        self.p_rgh = ZeroGradient() if not p_rgh else p_rgh

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
        U = FixedValue('(0 0 0)') if not U else U
        p = ZeroGradient() if not p else p
        k = KqRWallFunction('0.1') if not k else k
        epsilon = EpsilonWallFunction(0.01) \
            if not epsilon else epsilon
        nut = NutkWallFunction(0.01) \
            if not nut else nut
        T = T if T else None
        alphat = AlphatJayatillekeWallFunction(
            value='0', isUniform=True, Prt='0.85') if not alphat else alphat

        p_rgh = FixedFluxPressure(value='0', isUniform=True, rho='rhok') \
            if not p_rgh else p_rgh

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
        U = FixedValue('(0 0 0)') if not U else U
        p = ZeroGradient() if not p else p
        k = FixedValue('0.1') if not k else k
        epsilon = FixedValue('0.01') if not epsilon else epsilon
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
        U = ZeroGradient() if not U else U
        p = FixedValue('0') if not p else p
        k = ZeroGradient() if not k else k
        epsilon = ZeroGradient() if not epsilon else epsilon
        nut = Calculated('0')
        T = ZeroGradient() if not T else T
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
        U = FixedValue('(0 0 0)') if not U else U
        p = ZeroGradient() if not p else p
        k = KqRWallFunction('$internalField', isUnifrom=False) if not k else k
        epsilon = EpsilonWallFunction('$internalField', isUnifrom=False) \
            if not epsilon else epsilon
        nut = NutkWallFunction('0.0') \
            if not nut else nut
        T = ZeroGradient() if not T else FixedValue(T)
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
        U = FixedValue('(0 0 0)') if not U else U
        p = ZeroGradient() if not p else p
        k = ZeroGradient() if not k else k
        epsilon = ZeroGradient() if not epsilon else epsilon
        nut = NutkAtmRoughWallFunction.fromABLConditions(ablConditions,
                                                         'uniform 0')
        T = ZeroGradient() if not T else FixedValue(T)

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
        p = ZeroGradient() if not p else p
        nut = Calculated('0') if not nut else nut
        T = ZeroGradient() if not T else FixedValue(T)

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
        U = InletOutlet('uniform (0 0 0)', '$internalField') if not U else U
        p = FixedValue('$pressure') if not p else p
        k = InletOutlet('uniform $turbulentKE', '$internalField') \
            if not k else k
        epsilon = InletOutlet('uniform $turbulentEpsilon', '$internalField') \
            if not epsilon else epsilon
        nut = Calculated('0') if not nut else nut
        T = ZeroGradient() if not T else FixedValue(T)

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
        U = Slip() if not U else U
        p = Slip() if not p else p
        k = Slip() if not k else k
        epsilon = Slip() if not epsilon else epsilon
        nut = Calculated('0')
        T = ZeroGradient() if not T else FixedValue(T)

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
