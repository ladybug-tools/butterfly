# coding=utf-8
"""Butterfly wind tunnel class for Dynamo."""
import butterfly.windtunnel
from butterfly.z0 import Z0

from .case import Case
from .unitconversion import convertDocumentUnitsToMeters


class WindTunnelDS(butterfly.windtunnel.WindTunnel):
    u"""A dynamo wind tunnel.

    Args:
        geometries: List of butterfly geometries that will be inside the tunnel.
        windVector: Wind vector as a Vector3D. The length of the vector will be
            used as wind speed in m/s at Zref.
        tunnelParameters: Butterfly tunnel parameters.
        landscape: An integer between 0-7 to calculate roughness [z0] (default: 7).
            You can find full description of the landscape in Table I at this
            link: (http://onlinelibrary.wiley.com/doi/10.1002/met.273/pdf)

            0 > '0.0002'  # sea. Open sea or lake (irrespective of wave size),
            tidal flat, snow-covered flat plain, featureless desert, tarmac and
            concrete, with a free fetch of several kilometres

            1 > '0.005'   # smooth. Featureless land surface without any noticeable
            obstacles and with negligible vegetation; e.g. beaches, pack ice without
            large ridges, marsh and snow-covered or fallow open country.

            2 > '0.03'    # open. Level country with low vegetation (e.g. grass)
            and isolated obstacles with separations of at least 50 obstacle heights;
            e.g. grazing land without wind breaks, heather, moor and tundra,
            runway area of airports. Ice with ridges across-wind.

            3 > '0.10'    # roughly open. Cultivated or natural area with low crops
            or plant covers, or moderately open country with occasional obstacles
            (e.g. low hedges, isolated low buildings or trees) at relative horizontal
            distances of at least 20 obstacle heights

            4 > '0.25'    # rough. Cultivated or natural area with high crops or
            crops of varying height, and scattered obstacles at relative distances
            of 12-15 obstacle heights for porous objects (e.g. shelterbelts) or
            8–12 obstacle heights for low solid objects (e.g. buildings).

            5 > '0.5'     # very rough. Intensively cultivated landscape with many
            rather large obstacle groups (large farms, clumps of forest) separated
            by open spaces of about eight obstacle heights. Low densely planted
            major vegetation like bush land, orchards, young forest. Also, area
            moderately covered by low buildings with interspaces of three to
            seven building heights and no high trees.

            6 > '1.0'     # Skimming. Landscape regularly covered with similar-size
            large obstacles, with open spaces of the same order of magnitude as
            obstacle heights; e.g. mature regular forests, densely built-up area
            without much building height variation.

            7 > '2.0'     # chaotic. City centres with mixture of low-rise and
            high-rise buildings, or large forests of irregular height with many
            clearings.
        meshingparameters: Butterfly MeshingParameters.
        Zref: Reference height for wind velocity in meters (default: 10).
    """

    @classmethod
    def fromGeometriesWindVectorAndParameters(
        cls, name, geometries, windVector, tunnelParameters=None, landscape=1,
            meshingParameters=None, Zref=None):
        """Dynamo wind tunnel."""
        try:
            roughness = Z0()[landscape]
        except Exception as e:
            raise ValueError('Invalid input for landscape:{}\n{}'.format(
                landscape, e)
            )

        convertToMeters = convertDocumentUnitsToMeters()

        tunnelParameters = tunnelParameters or butterfly.windtunnel.TunnelParameters()

        windVector = (windVector.X, windVector.Y, windVector.Z)

        # init openFOAM windTunnel
        return super(WindTunnelDS, cls).fromGeometriesWindVectorAndParameters(
            name, geometries, windVector, tunnelParameters, roughness,
            meshingParameters, Zref, convertToMeters
        )

    def toOpenFOAMCase(self, make2dParameters=None):
        """Return a BF case for this wind tunnel."""
        return Case.fromWindTunnel(self, make2dParameters)
