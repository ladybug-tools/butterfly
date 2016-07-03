"""Butterfly wind tunnel."""
from blockMeshDict import BlockMeshDict
from z0 import Z0
from core import Case


class WindTunnel(object):
    """Butterfly WindTunnel.

    Args:
        inlet: Inlet as a honeybee surface. inlet boundary condition should be
            ABL (atmBoundaryLayer).
        outlet: Outlet as a butterfly surface.
        sides: Left and right side surfaces as butterfly surfaces.
        top: Top face as buttefly surface.
        ground: Ground face as butterfly surface.
        testGeomtries: A list of geometries as butterfly surfaces that are located
            within bounding box boundary.
        block: A butterfly Block for windtunnel bounding box.
        landscape: An integer between 0-7 to calculate z0 (roughness).
                0: '0.0002'  # sea
                1: '0.005'   # smooth
                2: '0.03'    # open
                3: '0.10'    # roughlyOpen
                4: '0.25'    # rough
                5: '0.5'     # veryRough
                6: '1.0'     # closed
                7: '2.0'     # chaotic
    """
    def __init__(inlet, outlet, sides, top, ground, testGeomtries,
                 block, landscape):
        """Init wind tunnel."""
        self.inlet = self.__checkIfBFSurface(inlet)
        self.outlet = self.__checkIfBFSurface(outlet)
        self.sides = tuple(side for side in sides if self.__checkIfBFSurface(side))
        self.top = self.__checkIfBFSurface(top)
        self.ground = self.__checkIfBFSurface(ground)
        self.testGeomtries = tuple(geo for geo in testGeomtries
                                   if self.__checkIfBFSurface(geo))

        self.block = block
        try:
            self.z0 = Z0()[landscape]
        except Exception as e:
            raise ValueError('Invalid input for landscape.\n{}'.format(landscape))

    @property
    def boundingSurfaces(self):
        """Return bounding surfaces of wind tunnel."""
        return (self.inlet, self.outlet) + self.sides + \
               (self.top, self.ground)

    def __checkIfBFSurface(self, input):
        if hasattr(input, 'isBFSurface'):
            return True
        else:
            raise ValueError('{} is not a Butterfly surface.'.format(input))

    @property
    def flowDir(self):
        """Get flow direction for this wind tunnel as a tuple (x, y, z)."""
        return self.inlet.flowDir

    @property
    def flowSpeed(self):
        """Get flow speed for this wind tunnel."""
        return self.inlet.Uref

    @property
    def zGround(self):
        """Minimum z value of the bounding box."""
        return self.block.minZ

    @property
    def blockMeshDict(self):
        """Wind tunnel blockMeshDict."""
        return BlockMeshDict(1, self.boundingSurfaces, [self.block])

    @property
    def ABLConditionsDict(self):
        """Get ABLCondition for this wind tunnel as a dictionary."""
        _ABLCDict = {}
        _ABLCDict['Uref'] = str(self.flowSpeed)
        _ABLCDict['z0'] = 'uniform {}'.format(self.z0)
        _ABLCDict['flowDir'] = '({} {} {})'.format(*self.flowDir)
        _ABLCDict['zGround'] = 'uniform {}'.format(self.zGround)
        return _ABLCDict

    def toCase(self):
        """Return a BF case for this wind tunnel."""
        pass


class TunnelParameters(object):
    """Wind tunnel parameters.

    Each parameter will be multiplied by multiple height.

    Args:
        windward: Multiplier value for windward extension (default: 3).
        top: Multiplier value for top extension (default: 3).
        side: Multiplier value for side extension (default: 3).
        leeward: Multiplier value for leeward extension (default: 3).
    """
    def __init__(self, windward=3, top=3, side=2, leeward=15):
        """Init wind tunnel parameters."""
        self.windward = self.__checkInput(windward)
        self.top = self.__checkInput(top)
        self.side = self.__checkInput(side)
        self.leeward = self.__checkInput(leeward)

    def __checkInput(self, input):
        """Check input values."""
        try:
            _inp = float(input)
        except:
            raise ValueError("Failed to convert %s to a number." % input)
        else:
            assert _inp > 0, "Value (%.2f) should be larger than 0." % _inp
            return _inp

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'WW: %.1fX; T: %.1fX; S: %.1fX; LW: %.1fX;' % (
                self.windward, self.top, self.side, self.leeward)
