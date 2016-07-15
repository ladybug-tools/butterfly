"""snappyHexMeshDict class."""
from foamfile import FoamFile
from collections import OrderedDict
from helper import getSnappyHexMeshGeometryFeild, \
    getSnappyHexMeshRefinementSurfaces


# TODO: Move default values into a separate file.
# TODO: Add specific methods to access most common values
class SnappyHexMeshDict(FoamFile):
    """Control dict class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['castellatedMesh'] = 'true'
    __defaultValues['snap'] = 'true'
    __defaultValues['addLayers'] = 'false'

    # geometry
    __defaultValues['geometry'] = {}

    # castellatedMeshControls
    __defaultValues['castellatedMeshControls'] = OrderedDict()
    __defaultValues['castellatedMeshControls']['maxLocalCells'] = '1000000'
    __defaultValues['castellatedMeshControls']['maxGlobalCells'] = '2000000'
    __defaultValues['castellatedMeshControls']['minRefinementCells'] = '10'
    __defaultValues['castellatedMeshControls']['maxLoadUnbalance'] = '0.10'
    __defaultValues['castellatedMeshControls']['nCellsBetweenLevels'] = '3'
    __defaultValues['castellatedMeshControls']['features'] = '()'
    __defaultValues['castellatedMeshControls']['refinementSurfaces'] = {}
    __defaultValues['castellatedMeshControls']['resolveFeatureAngle'] = '30'
    __defaultValues['castellatedMeshControls']['refinementRegions'] = {}
    __defaultValues['castellatedMeshControls']['locationInMesh'] = '(0 0 0)'
    __defaultValues['castellatedMeshControls']['allowFreeStandingZoneFaces'] = 'true'

    # snap controls
    __defaultValues['snapControls'] = OrderedDict()
    __defaultValues['snapControls']['nSmoothPatch'] = '3'
    __defaultValues['snapControls']['tolerance'] = '2'
    __defaultValues['snapControls']['nSolveIter'] = '30'
    __defaultValues['snapControls']['nRelaxIter'] = '5'
    __defaultValues['snapControls']['implicitFeatureSnap'] = 'true'
    __defaultValues['snapControls']['multiRegionFeatureSnap'] = 'true'

    # layer control
    __defaultValues['addLayersControls'] = OrderedDict()
    __defaultValues['addLayersControls']['relativeSizes'] = 'true'
    __defaultValues['addLayersControls']['layers'] = {}
    __defaultValues['addLayersControls']['expansionRatio'] = '1.0'
    __defaultValues['addLayersControls']['finalLayerThickness'] = '0.3'
    __defaultValues['addLayersControls']['minThickness'] = '0.2'
    __defaultValues['addLayersControls']['nGrow'] = '0'
    __defaultValues['addLayersControls']['featureAngle'] = '60'
    __defaultValues['addLayersControls']['nRelaxIter'] = '3'
    __defaultValues['addLayersControls']['nSmoothSurfaceNormals'] = '1'
    __defaultValues['addLayersControls']['nSmoothThickness'] = '10'
    __defaultValues['addLayersControls']['nSmoothNormals'] = '3'
    __defaultValues['addLayersControls']['maxFaceThicknessRatio'] = '0.5'
    __defaultValues['addLayersControls']['maxThicknessToMedialRatio'] = '0.3'
    __defaultValues['addLayersControls']['minMedianAxisAngle'] = '90'
    __defaultValues['addLayersControls']['nBufferCellsNoExtrude'] = '0'
    __defaultValues['addLayersControls']['nLayerIter'] = '50'
    __defaultValues['addLayersControls']['nRelaxedIter'] = '20'

    __defaultValues['meshQualityControls'] = OrderedDict()
    __defaultValues['meshQualityControls']['maxNonOrtho'] = '60'
    __defaultValues['meshQualityControls']['maxBoundarySkewness'] = '20'
    __defaultValues['meshQualityControls']['maxInternalSkewness'] = '4'
    __defaultValues['meshQualityControls']['maxConcave'] = '80'
    __defaultValues['meshQualityControls']['minFlatness'] = '0.5'
    __defaultValues['meshQualityControls']['minVol'] = '1e-13'
    __defaultValues['meshQualityControls']['minTetQuality'] = '1e-15'
    __defaultValues['meshQualityControls']['minArea'] = '-1'
    __defaultValues['meshQualityControls']['minTwist'] = '0.02'
    __defaultValues['meshQualityControls']['minDeterminant'] = '0.001'
    __defaultValues['meshQualityControls']['minFaceWeight'] = '0.02'
    __defaultValues['meshQualityControls']['minVolRatio'] = '0.01'
    __defaultValues['meshQualityControls']['minTriangleTwist'] = '-1'
    __defaultValues['meshQualityControls']['nSmoothScale'] = '4'
    __defaultValues['meshQualityControls']['errorReduction'] = '0.75'

    __defaultValues['debug'] = '0'
    __defaultValues['mergeTolerance'] = '1E-6'

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='snappyHexMeshDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromBFSurfaces(cls, projectName, BFSurfaces, globalRefinementLevel,
                       locationInMesh, meshingType='triSurfaceMesh',
                       values=None):
        """Create snappyHexMeshDict from HBSurfaces."""
        _cls = cls(values)
        _cls.locationInMesh = locationInMesh
        _cls.setGeometry(projectName, BFSurfaces, meshingType)
        _cls.setRefinementSurfaces(projectName, BFSurfaces, globalRefinementLevel)
        return _cls

    @property
    def locationInMesh(self):
        """A tuple for the location of the volume the should be meshed."""
        return self.values['castellatedMeshControls']['locationInMesh']

    @locationInMesh.setter
    def locationInMesh(self, point):
        if not point:
            point = (0, 0, 0)

        try:
            self.values['castellatedMeshControls']['locationInMesh'] = \
                str(tuple(eval(point))).replace(',', "")
        except:
            self.values['castellatedMeshControls']['locationInMesh'] = \
                str(tuple(point)).replace(',', "")

    @property
    def castellatedMesh(self):
        """Set if castellatedMesh should be ran."""
        return self.values['castellatedMesh']

    @castellatedMesh.setter
    def castellatedMesh(self, value=True):
        value = value if isinstance(value, bool) else \
            bool(str(value).capitalize())
        self.values['castellatedMesh'] = str(value).lower()

    @property
    def snap(self):
        """Set if snap should be ran."""
        return self.values['snap']

    @snap.setter
    def snap(self, value=True):
        value = value if isinstance(value, bool) else \
            bool(str(value).capitalize())
        self.values['snap'] = str(value).lower()

    @property
    def addLayers(self):
        """Set if addLayers should be ran."""
        return self.values['addLayers']

    @addLayers.setter
    def addLayers(self, value=True):
        value = value if isinstance(value, bool) else \
            bool(str(value).capitalize())
        self.values['addLayers'] = str(value).lower()

    @property
    def maxGlobalCells(self):
        """Set if addLayers should be ran."""
        return self.values['castellatedMeshControls']['maxGlobalCells']

    @maxGlobalCells.setter
    def maxGlobalCells(self, value=2000000):
        self.values['castellatedMeshControls']['maxGlobalCells'] = str(int(value))

    def setGeometry(self, projectName, BFSurfaces, meshingType='triSurfaceMesh'):
        """Set geometry from BFSurfaces."""
        _geoField = getSnappyHexMeshGeometryFeild(projectName, BFSurfaces,
                                                  meshingType)
        self.values['geometry'] = _geoField

    def setRefinementSurfaces(self, projectName, BFSurfaces, globalLevels):
        """Set refinement values for surfaces.

        Args:
            projectName: Name of OpenFOAM case.
            BFSurfaces: List of Butterfly surfaces.
            globalLevels: Default Min, max level of surface mesh refinement.
        """
        _ref = getSnappyHexMeshRefinementSurfaces(projectName,
                                                  BFSurfaces, globalLevels)

        self.values['castellatedMeshControls']['refinementSurfaces'] = _ref
