"""Butterfly Solution."""


class SolutionParameters(object):
    """A collection of parameters that can be adjusted in run-time.

    Attributes:
        controlDict: Control ditctionary.
        residualControl: Residual control values.
        probes: Butterfly probes.
    """

    def __init__(self, controlDict, residualControl, probes):
        """Initiate class."""
        self.controlDict = controlDict
        self.residualControl = residualControl
        self.probes = probes

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Class representation."""
        return self.__class__.__name__
