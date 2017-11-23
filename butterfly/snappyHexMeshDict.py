# coding=utf-8
"""snappyHexMeshDict class."""
from collections import OrderedDict
import re

from .foamfile import FoamFile, foam_file_from_file
from .utilities import get_snappyHexMesh_geometry_feild, \
    get_snappyHexMesh_refinement_surfaces, get_snappyHexMesh_surface_layers
from .refinementRegion import refinement_mode_from_dict


# TODO(mostapha): Move default values into a separate file.
# TODO(mostapha): Add specific methods to access most common values
class SnappyHexMeshDict(FoamFile):
    """Control dict class."""

    # set default valus for this class
    __default_values = OrderedDict()
    __default_values['castellatedMesh'] = 'true'
    __default_values['snap'] = 'true'
    __default_values['addLayers'] = 'false'

    # geometry
    __default_values['geometry'] = {}

    # castellatedMeshControls
    __default_values['castellatedMeshControls'] = OrderedDict()
    __default_values['castellatedMeshControls']['maxLocalCells'] = '1000000'
    __default_values['castellatedMeshControls']['maxGlobalCells'] = '2000000'
    __default_values['castellatedMeshControls']['minRefinementCells'] = '10'
    __default_values['castellatedMeshControls']['maxLoadUnbalance'] = '0.10'
    __default_values['castellatedMeshControls']['nCellsBetweenLevels'] = '3'
    __default_values['castellatedMeshControls']['features'] = '()'
    __default_values['castellatedMeshControls']['refinementSurfaces'] = {}
    __default_values['castellatedMeshControls']['resolveFeatureAngle'] = '180'
    __default_values['castellatedMeshControls']['refinementRegions'] = {}
    __default_values['castellatedMeshControls']['locationInMesh'] = '(0 0 0)'
    __default_values['castellatedMeshControls']['allowFreeStandingZoneFaces'] = 'true'

    # snap controls
    __default_values['snapControls'] = OrderedDict()
    __default_values['snapControls']['nSmoothPatch'] = '5'
    __default_values['snapControls']['tolerance'] = '5'
    __default_values['snapControls']['nSolveIter'] = '100'
    __default_values['snapControls']['nRelaxIter'] = '8'
    __default_values['snapControls']['nFeatureSnapIter'] = '10'
    __default_values['snapControls']['extractFeaturesRefineLevel'] = None
    __default_values['snapControls']['explicitFeatureSnap'] = None
    __default_values['snapControls']['implicitFeatureSnap'] = 'true'
    __default_values['snapControls']['multiRegionFeatureSnap'] = 'true'

    # layer control
    __default_values['addLayersControls'] = OrderedDict()
    __default_values['addLayersControls']['relativeSizes'] = 'true'
    __default_values['addLayersControls']['layers'] = {}
    __default_values['addLayersControls']['expansionRatio'] = '1.0'
    __default_values['addLayersControls']['finalLayerThickness'] = '0.3'
    __default_values['addLayersControls']['minThickness'] = '0.2'
    __default_values['addLayersControls']['nGrow'] = '0'
    __default_values['addLayersControls']['featureAngle'] = '110'
    __default_values['addLayersControls']['nRelaxIter'] = '3'
    __default_values['addLayersControls']['nSmoothSurfaceNormals'] = '1'
    __default_values['addLayersControls']['nSmoothThickness'] = '10'
    __default_values['addLayersControls']['nSmoothNormals'] = '3'
    __default_values['addLayersControls']['maxFaceThicknessRatio'] = '0.5'
    __default_values['addLayersControls']['maxThicknessToMedialRatio'] = '0.3'
    __default_values['addLayersControls']['minMedianAxisAngle'] = '130'
    __default_values['addLayersControls']['nBufferCellsNoExtrude'] = '0'
    __default_values['addLayersControls']['nLayerIter'] = '50'
    __default_values['addLayersControls']['nRelaxedIter'] = '20'

    __default_values['meshQualityControls'] = OrderedDict()
    __default_values['meshQualityControls']['maxNonOrtho'] = '60'
    __default_values['meshQualityControls']['maxBoundarySkewness'] = '20'
    __default_values['meshQualityControls']['maxInternalSkewness'] = '4'
    __default_values['meshQualityControls']['maxConcave'] = '80'
    __default_values['meshQualityControls']['minFlatness'] = '0.5'
    __default_values['meshQualityControls']['minVol'] = '1e-13'
    __default_values['meshQualityControls']['minTetQuality'] = '1e-15'
    __default_values['meshQualityControls']['minArea'] = '-1'
    __default_values['meshQualityControls']['minTwist'] = '0.02'
    __default_values['meshQualityControls']['minDeterminant'] = '0.001'
    __default_values['meshQualityControls']['minFaceWeight'] = '0.02'
    __default_values['meshQualityControls']['minVolRatio'] = '0.01'
    __default_values['meshQualityControls']['minTriangleTwist'] = '-1'
    __default_values['meshQualityControls']['nSmoothScale'] = '4'
    __default_values['meshQualityControls']['errorReduction'] = '0.75'
    __default_values['meshQualityControls']['relaxed'] = {'maxNonOrtho': '75'}

    __default_values['debug'] = '0'
    __default_values['mergeTolerance'] = '1E-6'
    __globRefineLevel = (0, 0)

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='snappyHexMeshDict', cls='dictionary',
                          location='system', default_values=self.__default_values,
                          values=values)
        self.__geometries = None
        self.__isFeatureEdgeRefinementImplicit = True
        self.convertToMeters = 1.0  # This is useful to scale the locationInMesh

    @classmethod
    def from_file(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foam_file_from_file(filepath, cls.__name__))

    @classmethod
    def from_bf_geometries(cls, project_name, geometries, meshing_parameters=None,
                           convertToMeters=1, values=None):
        """Create snappyHexMeshDict from HBGeometries."""
        _cls = cls(values)
        _cls.convertToMeters = convertToMeters
        _cls.project_name = project_name
        _cls.__geometries = cls._check_input_geometries(geometries)
        _cls.update_meshing_parameters(meshing_parameters)
        _cls.set_geometry()
        _cls.set_refinement_surfaces()
        _cls.set_nSurfaceLayers()
        return _cls

    @property
    def project_name(self):
        """Project name."""
        return self.__project_name

    # TODO(mostapha): updating the name should update refinementSurfaces and setGeometry
    # when happens from Case.from_file() with no butterfly geometry.
    @project_name.setter
    def project_name(self, name):
        assert re.match("^[a-zA-Z0-9_]*$", name), \
            'Invalid project name: "{}".\n' \
            'Do not use whitespace or special charecters.'.format(name)
        self.__project_name = name

    @property
    def geometries(self):
        """Butterfly geometries."""
        return self.__geometries

    @property
    def is_featureEdgeRefinement_implicit(self):
        """Return True if implicit feature refinment is used."""
        return self.__isFeatureEdgeRefinementImplicit

    @property
    def locationInMesh(self):
        """A tuple for the location of the volume the should be meshed.

        x, y, z values will be multiplied to self.convertToMeters. If the units
        are not Meters you can set the convertToMeters using self.convertToMeters
        """
        return self.values['castellatedMeshControls']['locationInMesh']

    @locationInMesh.setter
    def locationInMesh(self, point):
        if not point:
            point = (0, 0, 0)

        try:
            x, y, z = tuple(eval(point))
        except Exception:
            x, y, z = tuple(point)

        # scale point based on convertToMeters
        point = x * self.convertToMeters, \
            y * self.convertToMeters, \
            z * self.convertToMeters

        self.values['castellatedMeshControls']['locationInMesh'] = \
            str(tuple(point)).replace(',', "")

    @property
    def globRefineLevel(self):
        """A tuple of (min, max) values for global refinment."""
        return self.__globRefineLevel

    @globRefineLevel.setter
    def globRefineLevel(self, r):
        self.__globRefineLevel = (0, 0) if not r else tuple(r)
        if self.__globRefineLevel:
            self.set_refinement_surfaces()

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
    def features(self):
        """Set features for castellatedMeshControls."""
        return self.values['castellatedMeshControls']['features']

    @features.setter
    def features(self, value=None):
        value = value or ()
        self.values['castellatedMeshControls']['features'] = str(value)

    @property
    def extractFeaturesRefineLevel(self):
        """A refinment value for extract feature level."""
        return self.values['snapControls']['extractFeaturesRefineLevel']

    @extractFeaturesRefineLevel.setter
    def extractFeaturesRefineLevel(self, value=1):
        self.values['snapControls']['extractFeaturesRefineLevel'] = str(int(value))

    @property
    def nCellsBetweenLevels(self):
        """Number of cells between levels for castellatedMeshControls (default: 3)."""
        return self.values['castellatedMeshControls']['nCellsBetweenLevels']

    @nCellsBetweenLevels.setter
    def nCellsBetweenLevels(self, value=3):
        value = value or 3
        self.values['castellatedMeshControls']['nCellsBetweenLevels'] = str(int(value))

    @property
    def maxGlobalCells(self):
        """Number of max global cells for castellatedMeshControls (default: 2000000)."""
        return self.values['castellatedMeshControls']['maxGlobalCells']

    @maxGlobalCells.setter
    def maxGlobalCells(self, value=2000000):
        value = value or 2000000
        self.values['castellatedMeshControls']['maxGlobalCells'] = str(int(value))

    @property
    def stl_file_names(self):
        """List of names for stl files if any.

        This method doesn't return stl files for refinementRegions. You can use
        self.refinementRegion_names to get the names for refinment regions.
        """
        stl_f_names = self.values['geometry'].keys()
        return tuple(f[:-4] for f in stl_f_names
                     if not f[:-4] in self.refinementRegion_names)

    @property
    def refinementRegions(self):
        """Refinement regions."""
        return self.values['castellatedMeshControls']['refinementRegions']

    @property
    def refinementRegion_names(self):
        """List of stl files if any."""
        return self.values['castellatedMeshControls']['refinementRegions'].keys()

    def update_meshing_parameters(self, meshing_parameters):
        """Update meshing parameters for blockMeshDict."""
        if not meshing_parameters:
            return

        assert hasattr(meshing_parameters, 'isMeshingParameters'), \
            'Expected MeshingParameters not {}'.format(type(meshing_parameters))

        if meshing_parameters.locationInMesh:
            self.locationInMesh = meshing_parameters.locationInMesh

        if meshing_parameters.globRefineLevel:
            self.globRefineLevel = meshing_parameters.globRefineLevel

    def refinementRegion_mode(self, refinementRegion_name):
        """Refinement region mode for a refinement region."""
        assert refinementRegion_name in self.refinementRegion_names, \
            'Failed to find {} in {}'.format(refinementRegion_name,
                                             self.refinementRegion_names)

        c_mesh_control = self.values['castellatedMeshControls']
        mode = c_mesh_control['refinementRegions'][refinementRegion_name]
        return refinement_mode_from_dict(mode)

    def set_geometry(self):
        """Set geometry from bf_geometries."""
        _geoField = get_snappyHexMesh_geometry_feild(self.project_name,
                                                     self.geometries,
                                                     meshing_type='triSurfaceMesh')
        self.values['geometry'].update(_geoField)

    def set_refinement_surfaces(self):
        """Set refinement values for geometries."""
        _ref = get_snappyHexMesh_refinement_surfaces(self.project_name,
                                                     self.geometries,
                                                     self.globRefineLevel)

        self.values['castellatedMeshControls']['refinementSurfaces'] = _ref

    def set_nSurfaceLayers(self):
        """Set number of surface layers for geometries."""
        layers = get_snappyHexMesh_surface_layers(self.geometries)
        self.values['addLayersControls']['layers'] = layers

    def set_featureEdgeRefinement_to_implicit(self):
        """Set meshing snap to implicitFeatureSnap."""
        self.values['snapControls']['implicitFeatureSnap'] = 'true'
        self.values['snapControls']['multiRegionFeatureSnap'] = 'true'
        self.values['snapControls']['explicitFeatureSnap'] = None
        self.values['snapControls']['extractFeaturesRefineLevel'] = None
        self.values['castellatedMeshControls']['features'] = '()'
        self.__isFeatureEdgeRefinementImplicit = True

    def set_featureEdgeRefinement_to_explicit(self, file_name, refinement_level=2):
        """Set meshing snap to explicitFeatureSnap.

        Args:
            file_name: eMesh file name.
            refinement_level: extractFeaturesRefineLevel (default: 2)
        """
        file_name = file_name.replace('.eMesh', '')

        if hasattr(refinement_level, 'levels'):
            # in case it's a distance refinment
            refinement_level = refinement_level.levels
        else:
            refinement_level = refinement_level or 2

        self.values['castellatedMeshControls']['features'] = \
            '({file "%s.eMesh"; level %s;} )' % (file_name, str(refinement_level))

        self.values['snapControls']['implicitFeatureSnap'] = None
        self.values['snapControls']['multiRegionFeatureSnap'] = None
        self.values['snapControls']['explicitFeatureSnap'] = 'true'
        self.values['snapControls']['extractFeaturesRefineLevel'] = 'true'

        self.__isFeatureEdgeRefinementImplicit = False

    def add_stl_geometry(self, file_name):
        """Add stl geometry to snappyHexMeshDict.

        Args:
            file_name: Stl file name. This file should be located under
                /constant/triSurface.
        """
        stl = {'{}.stl'.format(file_name): {'type': 'triSurfaceMesh',
                                            'name': file_name}}

        self.values['geometry'].update(stl)

    def add_refinementRegion(self, refinementRegion=None):
        """Add refinement region to snappyHexMeshDict."""
        if refinementRegion is None:
            return

        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            '{} is not a refinement region.'.format(refinementRegion)

        # add geometry to stl
        self.add_stl_geometry(refinementRegion.name)

        rg = {refinementRegion.name:
              refinementRegion.refinement_mode.to_openfoam_dict()}

        self.values['castellatedMeshControls']['refinementRegions'].update(rg)

    @staticmethod
    def _check_input_geometries(geos):
        for geo in geos:
            assert hasattr(geo, 'isBFMesh'), \
                'Expected butterfly.Mesh not {}'.format(geo)
        return geos
