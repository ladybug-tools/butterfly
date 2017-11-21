# coding=utf-8
"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from collections import OrderedDict
from fields import AtmBoundaryLayerInletVelocity, AtmBoundaryLayerInletK, \
    AtmBoundaryLayerInletEpsilon, Calculated, EpsilonWallFunction, FixedValue, \
    InletOutlet, KqRWallFunction, NutkWallFunction, NutkAtmRoughWallFunction, \
    Slip, ZeroGradient, AlphatJayatillekeWallFunction, FixedFluxPressure, Empty, \
    Field


class BoundaryCondition(object):
    """Boundary condition base class.
    """

    # TODO(Mostapha): Write a descriptor for each field and replace all properties
    def __init__(self, bc_type='patch', T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Instantiate boundary condition.
        Attributes:
                :param bc_type: Boundary condition type. e.g.(patch, wall)
                :param T: Optional input for temperature in Kelvin (300)
                :param U: OpenFOAM value for U.
                :param p: OpenFOAM value for p.
                :param k: OpenFOAM value for k.
                :param epsilon: OpenFOAM value for epsilon.
                :param nut: OpenFOAM value for nut.
        """
        self.__dict__['is{}'.format(self.__class__.__name__)] = True
        self.type = bc_type
        # set default values
        self.T = T
        self.U = U
        self.p = p
        self.k = k
        self.epsilon = epsilon
        self.nut = nut
        self.alphat = alphat
        self.p_rgh = p_rgh

    @property
    def T(self):
        "T boundary condition."
        return self._T

    @T.setter
    def T(self, t):
        self._T = self.try_get_field(t or ZeroGradient())

    @property
    def U(self):
        "U boundary condition."
        return self._U

    @U.setter
    def U(self, u):
        self._U = self.try_get_field(u or ZeroGradient())

    @property
    def p(self):
        "p boundary condition."
        return self._p

    @p.setter
    def p(self, p):
        self._p = self.try_get_field(p or ZeroGradient())

    @property
    def k(self):
        "k boundary condition."
        return self._k

    @k.setter
    def k(self, k_):
        self._k = self.try_get_field(k_ or ZeroGradient())

    @property
    def epsilon(self):
        "epsilon boundary condition."
        return self._epsilon

    @epsilon.setter
    def epsilon(self, e):
        self._epsilon = self.try_get_field(e or ZeroGradient())

    @property
    def nut(self):
        "nut boundary condition."
        return self._nut

    @nut.setter
    def nut(self, n):
        self._nut = self.try_get_field(n or ZeroGradient())

    @property
    def alphat(self):
        "alphat boundary condition."
        return self._alphat

    @alphat.setter
    def alphat(self, a):
        self._alphat = self.try_get_field(a or ZeroGradient())

    @property
    def p_rgh(self):
        "p_rgh boundary condition."
        return self._p_rgh

    @p_rgh.setter
    def p_rgh(self, prgh):
        self._p_rgh = self.try_get_field(prgh or ZeroGradient())

    def isBoundaryCondition(self):
        """Return True for boundary conditions."""
        return True

    @staticmethod
    def try_get_field(f):
        """Try getting the field from the input.

        The method will return the input if it is an instance of class <Field>,
        otherwise it tries to create the field from a dictionary and finally
        tries to create it from the string.
        """
        if isinstance(f, Field):
            return f
        elif isinstance(f, (dict, OrderedDict)):
            return Field.from_dict(f)
        else:
            try:
                return Field.from_string(f)
            except Exception:
                raise ValueError(
                    'Failed to create an OpenFOAM field from {}. Use a valid value.'
                    .format(f))

    def duplicate(self):
        """Duplicate Boundary Condition."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}".format(self.__class__.__name__, self.type)


class BoundingBoxBoundaryCondition(BoundaryCondition):
    """Bounding box boundary condition for bounding box geometry.

    It returns a boundary condition of ZeroGradient for all the inputs.
    """

    def __init__(self):
        """Init bounday condition."""
        U = ZeroGradient()
        p = ZeroGradient()
        k = ZeroGradient()
        epsilon = ZeroGradient()
        nut = ZeroGradient()
        T = ZeroGradient()
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()
        super(BoundingBoxBoundaryCondition, self).__init__(
            'wall', T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class EmptyBoundaryCondition(BoundaryCondition):
    """Empty boundary condition.

    It returns a boundary condition of Empty for all the inputs.
    """

    def __init__(self):
        """Init bounday condition."""
        U = Empty()
        p = Empty()
        k = Empty()
        epsilon = Empty()
        nut = Empty()
        T = Empty()
        alphat = Empty()
        p_rgh = Empty()
        super(EmptyBoundaryCondition, self).__init__(
            'wall', T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class IndoorWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition base class.

    Attributes:
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None,
                 alphat=None, p_rgh=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('0.1')
        epsilon = epsilon or EpsilonWallFunction(0.01)
        nut = nut or NutkWallFunction(0.01)
        T = T or ZeroGradient()
        alphat = alphat or AlphatJayatillekeWallFunction(
            value='0', is_uniform=True, Prt='0.85')

        p_rgh = p_rgh or FixedFluxPressure(value='0', is_uniform=True, rho='rhok')

        BoundaryCondition.__init__(self, 'wall', T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)


class FixedInletBoundaryCondition(BoundaryCondition):
    """Inlet boundary condition base class.

    Attributes:
        T: Optional input for Temperature.
        U: Air velocity as fixed value (x, y, z).
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None,
                 alphat=None, p_rgh=None):
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

        BoundaryCondition.__init__(self, 'patch', T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}".format(
            self.__class__.__name__, self.type, self.U)


class FixedOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition base class.

    Attributes:
        pressure: Pressure as a float (default: 0)
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None,
                 alphat=None, p_rgh=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or InletOutlet(value='uniform (0 0 0)', inletValue='uniform (0 0 0)')
        p = p or FixedValue('0')
        k = k or InletOutlet(value='uniform 0.1', inletValue='uniform 0.1')
        epsilon = epsilon or InletOutlet(value='uniform 0.1', inletValue='uniform 0.1')
        nut = Calculated('0')
        T = T or ZeroGradient()
        alphat = alphat or ZeroGradient()
        p_rgh = p_rgh or FixedValue('0')

        super(FixedOutletBoundaryCondition, self).__init__(
            'patch', T, U, p, k, epsilon, nut, alphat, p_rgh
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}".format(
            self.__class__.__name__, self.type, self.p)


class WindTunnelWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition for wall geometrys inside wind tunnel.

    Attributes:
        T: Optional input for Temperature.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('$internalField', is_unifrom=False)
        epsilon = epsilon or EpsilonWallFunction('$internalField', is_unifrom=False)
        nut = nut or NutkWallFunction('0.0')
        T = T or ZeroGradient()
        super(WindTunnelWallBoundaryCondition, self).__init__(
            'wall', T, U, p, k, epsilon, nut
        )


class WindTunnelGroundBoundaryCondition(BoundaryCondition):
    """Wind tunnel ground boundary condition.

    Attributes:
        T: Optional input for Temperature.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ABLConditions, T=None, U=None, p=None, k=None, epsilon=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or ZeroGradient()
        epsilon = epsilon or ZeroGradient()
        nut = NutkAtmRoughWallFunction.from_ABLConditions(ABLConditions,
                                                          'uniform 0')
        T = T or ZeroGradient()

        super(WindTunnelGroundBoundaryCondition, self).__init__(
            'wall', T, U, p, k, epsilon, nut
        )


class WindTunnelInletBoundaryCondition(BoundaryCondition):
    """Wind tunnel atmBoundaryLayerInletVelocity boundary condition.

    Attributes:
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ABLConditions, T=None, p=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = AtmBoundaryLayerInletVelocity.from_ABLConditions(ABLConditions)
        k = AtmBoundaryLayerInletK.from_ABLConditions(ABLConditions)
        epsilon = AtmBoundaryLayerInletEpsilon.from_ABLConditions(ABLConditions)
        p = p or ZeroGradient()
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelInletBoundaryCondition, self).__init__(
            'patch', T, U, p, k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}".format(
            self.__class__.__name__, self.type, self.U.Uref)


class WindTunnelOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or InletOutlet('uniform (0 0 0)', '$internalField')
        p = p or FixedValue('$pressure')
        k = k or InletOutlet('uniform $turbulentKE', '$internalField')
        epsilon = epsilon or InletOutlet('uniform $turbulentEpsilon', '$internalField')
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelOutletBoundaryCondition, self).__init__(
            'patch', T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}".format(
            self.__class__.__name__, self.type, self.p)


class WindTunnelTopAndSidesBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for top and sides of wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, T=None, U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or Slip()
        p = p or Slip()
        k = k or Slip()
        epsilon = epsilon or Slip()
        nut = Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelTopAndSidesBoundaryCondition, self).__init__(
            'patch', T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}".format(self.__class__.__name__, self.type)


if __name__ == '__main__':
    from conditions import ABLConditions
    abc = ABLConditions()
    print(WindTunnelWallBoundaryCondition())
    print(WindTunnelInletBoundaryCondition(abc))
    print(WindTunnelGroundBoundaryCondition(abc))
