# coding=utf-8
"""snappyHexMeshDict class."""
from collections import OrderedDict
import re

from .foamfile import FoamFile, foamFileFromFile
from .utilities import getSnappyHexMeshGeometryFeild, \
    getSnappyHexMeshRefinementSurfaces
from .refinementRegion import refinementModeFromDict


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
    __globRefineLevel = (1, 1)

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='snappyHexMeshDict', cls='dictionary',
                          location='system', defaultValues=self.__defaultValues,
                          values=values)
        self.__geometries = None

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    @classmethod
    def fromBFGeometries(cls, projectName, geometries, meshingParameters=None,
                         values=None):
        """Create snappyHexMeshDict from HBGeometries."""
        _cls = cls(values)
        _cls.projectName = projectName
        _cls.__geometries = cls.__checkInputGeometries(geometries)
        _cls.updateMeshingParameters(meshingParameters)
        _cls.setGeometry()
        _cls.setRefinementSurfaces()
        return _cls

    @property
    def projectName(self):
        """Project name."""
        return self.__projectName

    # TODO: updating the name should update refinementSurfaces and setGeometry
    # when happens from Case.fromFile() with no butterfly geometry.
    @projectName.setter
    def projectName(self, name):
        assert re.match("^[a-zA-Z0-9_]*$", name), \
            'Invalid project name: "{}".\n' \
            'Do not use whitespace or special charecters.'.format(name)
        self.__projectName = name

    @property
    def geometries(self):
        """Butterfly geometries."""
        return self.__geometries

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
    def globRefineLevel(self):
        """A tuple of (min, max) values for global refinment."""
        return self.__globRefineLevel

    @globRefineLevel.setter
    def globRefineLevel(self, r):
        self.globRefineLevel = (1, 1) if not r else tuple(r)
        if r:
            _cls.setRefinementSurfaces()

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

    @property
    def stlFileNames(self):
        """List of stl files if any."""
        stlFNames = self.values['geometry'].keys()
        return tuple(f[:-4] for f in stlFNames
                     if not f[:-4] in self.refinementRegionNames)

    @property
    def refinementRegions(self):
        """Refinement regions."""
        return self.values['castellatedMeshControls']['refinementRegions']

    @property
    def refinementRegionNames(self):
        """List of stl files if any."""
        return self.values['castellatedMeshControls']['refinementRegions'].keys()

    def updateMeshingParameters(self, meshingParameters):
        """Update meshing parameters for blockMeshDict."""
        if not meshingParameters:
            return

        assert hasattr(meshingParameters, 'isMeshingParameters'), \
            'Expected MeshingParameters not {}'.format(type(meshingParameters))

        if meshingParameters.locationInMesh:
            self.locationInMesh = meshingParameters.locationInMesh

        if meshingParameters.globRefineLevel:
            self.globRefineLevel = meshingParameters.globRefineLevel

    def refinementRegionMode(self, refinementRegionName):
        """Refinement region mode for a refinement region."""
        assert refinementRegionName in self.refinementRegionNames, \
            'Failed to find {} in {}'.format(refinementRegionName,
                                             self.refinementRegionNames)

        mode = self.values['castellatedMeshControls']['refinementRegions'][refinementRegionName]
        return refinementModeFromDict(mode)

    def setGeometry(self):
        """Set geometry from BFGeometries."""
        _geoField = getSnappyHexMeshGeometryFeild(self.projectName,
                                                  self.geometries,
                                                  meshingType='triSurfaceMesh')
        self.values['geometry'].update(_geoField)

    def setRefinementSurfaces(self):
        """Set refinement values for geometries."""
        _ref = getSnappyHexMeshRefinementSurfaces(self.projectName,
                                                  self.geometries,
                                                  self.globRefineLevel)

        self.values['castellatedMeshControls']['refinementSurfaces'] = _ref

    def addStlGeometry(self, fileName):
        """Add stl geometry to snappyHexMeshDict.

        Args:
            fileName: Stl file name. This file should be located under
                /constant/triSurface.
        """
        stl = {'{}.stl'.format(fileName): {'type': 'triSurfaceMesh',
                                           'name': fileName}}

        self.values['geometry'].update(stl)

    def addRefinementRegion(self, refinementRegion=None):
        """Add refinement region to snappyHexMeshDict."""
        # assert hasattr(refinementRegion, 'isRefinementRegion'), \
        #     '{} is not a refinement region.'.format(refinementRegion)

        # add geometry to stl
        self.addStlGeometry(refinementRegion.name)

        rg = {refinementRegion.name:
              refinementRegion.refinementMode.toOpenFOAMDict()}

        self.values['castellatedMeshControls']['refinementRegions'].update(rg)

    @staticmethod
    def __checkInputGeometries(geos):
        for geo in geos:
            assert hasattr(geo, 'isBFMesh'), \
                'Expected butterfly.Mesh not {}'.format(geo)
        return geos
