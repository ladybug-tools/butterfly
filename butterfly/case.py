"""Butterfly OpenFOAM Case."""
import os
import re  # to check input names
from shutil import rmtree  # to remove case folders if needed
from distutils.dir_util import copy_tree  # to copy sHM meshes over to tri
from collections import namedtuple
from copy import deepcopy
try:
    from itertools import izip as zip
except:
    # python 3
    pass
from .version import Version
from .utilities import load_case_files, load_probe_values_from_folder, \
    load_probes_from_postProcessing_file, load_probes_and_values_from_sample_file
from .geometry import bf_geometry_from_stl_file, calculate_min_max_from_bf_geometries
from .refinementRegion import refinementRegions_from_stl_file
from .meshingparameters import MeshingParameters
from .fields import Field

#
from .foamfile import FoamFile

# constant folder objects
from .turbulenceProperties import TurbulenceProperties
from .RASProperties import RASProperties
from .transportProperties import TransportProperties
from .g import G

# 0 folder objects
from .U import U
from .k import K
from .p import P
from .nut import Nut
from .epsilon import Epsilon
from .T import T
from .alphat import Alphat
from .p_rgh import P_rgh
from .conditions import ABLConditions, InitialConditions

# # system folder objects
from .blockMeshDict import BlockMeshDict
from .controlDict import ControlDict
from .snappyHexMeshDict import SnappyHexMeshDict
from .fvSchemes import FvSchemes
from .fvSolution import FvSolution
from .functions import Probes
from .decomposeParDict import DecomposeParDict
from .sampleDict import SampleDict

import butterfly

if butterfly.config['runner'] == 'blueCFD':
    from .runmanager_bluecfd import RunManagerBlueCFD as RunManager
else:
    from .runmanager import RunManager


class Case(object):
    """
    Principal class for OpenFOAM Cases.

    This class can either be instantiated directly through the __init__ constructor or
    through the following classmethods:

        1. from_folder: Create a Butterfly case from a case folder
        2. from_bf_geometries: Create a case from Butterfly geometries.
        3. from_wind_tunnel: Create case from wind tunnel.


    Notes for beginners:
        What is an OpenFOAM case?
            As defined by AndRAS Horvath in "OpenFOAM tutorial collection", a case is the
            combination of geometry definition (the finite volume mesh), configuration
            files (called dictionaries in OpenFOAM language), definition of boundary
            conditions and initial conditions, custom function and results all structured
            in many files and directories. The 0-directory contains the initial- and
            boundary-conditions. The (initial) mesh is in constant/polyMesh. Most config
            files are in system/. Material and turbulence properties are in
            constant/.

    """

    SUBFOLDERS = ('0', 'constant', 'constant\\polyMesh',
                  'constant\\triSurface', 'system', 'log')

    # minimum list of files to be able to run blockMesh and snappyHexMesh
    MINFOAMFIles = ('fvSchemes', 'fvSolution', 'controlDict', 'blockMeshDict',
                    'snappyHexMeshDict')

    def __init__(self, name, foamfiles, geometries):
        """Init case.

        Attributes:
        name: Case name as a string with no whitespace.

        :type name: str

        foamfiles: Collection of FoamFile objects (dictionaries) for this case.

        :type   foamfiles: FoamFile

        geometries: Collection of geometry-like objects. Geometries should have
            a name and toStlString method. The information related to boundary
            condition should already be included in related foamfiles. If you
            want to initiate the class form a folder or a number of bf_geometries
            use from_folder, and from_bf_geometries classmethods.

        """
        # original name is a variable to address the current limitation to change
        # the name of stl file in snappyHexMeshDict. It will be removed once the
        # limitation is addressed. The value wil be assigned in classmethod from_file
        self.__originalName = None

        self.project_name = name
        self.__version = float(Version.of_ver)
        self.decomposeParDict = None

        # optional input for changing working directory
        # should not be used on OpenFOAM on Windows
        self.working_dir = os.path.join(os.path.expanduser('~'), 'butterfly')

        # set foamfiles dynamically. This is flexible but makes documentation
        # tricky. also autocomplete won't work for this cases.
        self.__foamfiles = []
        self.add_foam_files(foamfiles)

        # set butterfly geometries
        self.__geometries = self._check_input_geometries(geometries)

        # place holder for refinment regions
        # use .add_refinementRegions to add regions to case
        self.__refinementRegions = []
        self.runmanager = RunManager(self.project_name)

    @classmethod
    def from_folder(cls, path, name=None, convert_from_meters=1):
        """Create a Butterfly case from a case folder.

        Args:
            path: Full path to case folder.
            name: An optional new name for this case.
            convert_from_meters: A number to be multiplied to stl file vertices
                to be converted to the new units if not meters. This value will
                be the inverse of convertToMeters.
        """
        # collect foam files
        __originalName = os.path.split(path)[-1]
        if not name:
            name = __originalName

        _files = load_case_files(path, fullpath=True)

        # convert files to butterfly objects
        ff = []
        for f in (_files.zero, _files.constant, _files.system):
            for p in f:
                if not p:
                    continue
                try:
                    ff.append(
                        cls.__create_foamfile_from_file(
                            p, 1.0 / convert_from_meters))
                    print('Imported {} from case.'.format(p))
                except Exception as e:
                    print('Failed to import {}:\n\t{}'.format(p, e))
        s_hmd = cls.__get_foam_file_by_name('snappyHexMeshDict', ff)

        if s_hmd:
            s_hmd.project_name = name

            stlfiles = tuple(f for f in _files.stl if f.lower().endswith('.stl'))
            bf_geometries = tuple(
                geo for f in stlfiles
                for geo in bf_geometry_from_stl_file(f, convert_from_meters)
                if os.path.split(f)[-1][:-4] in s_hmd.stl_file_names)

        else:
            bf_geometries = []

        _case = cls(name, ff, bf_geometries)

        # update each field of boundary condition for geometries
        for ff in _case.get_foam_files_from_location('0'):
            for geo in _case.geometries:
                try:
                    f = ff.get_boundary_field(geo.name)
                except AttributeError as e:
                    if not geo.name.endswith('Conditions'):
                        print(str(e))
                else:
                    # set boundary condition for the field
                    if not f:
                        setattr(geo.boundary_condition, ff.name, None)
                    else:
                        setattr(geo.boundary_condition, ff.name, Field.from_dict(f))

        if s_hmd:
            refinementRegions = tuple(
                ref for f in _files.stl
                if os.path.split(f)[-1][:-4] in s_hmd.refinementRegion_names
                for ref in refinementRegions_from_stl_file(
                    f, s_hmd.refinementRegion_mode(os.path.split(f)[-1][:-4]))
            )

            _case.add_refinementRegions(refinementRegions)

        # original name is a variable to address the current limitation to change
        # the name of stl file in snappyHexMeshDict. It will be removed once the
        # limitation is addressed.
        _case.__originalName = __originalName

        return _case

    @classmethod
    def from_bf_geometries(cls, name, geometries, blockMeshDict=None,
                           meshing_parameters=None, make2d_parameters=None,
                           convertToMeters=1):
        """Create a case from Butterfly geometries.

        foam_files/dictionaries will be generated based on boundary condition of
        geometries. fvSolution and fvSchemes will be set to default can can be
        overwritten once a Solution is created from a Case and a Recipe. You can
        overwrite them through the recipe.

        Args:
            name: Case name as a string with no whitespace.
            geometries: Collection of bf_geometries. FoamFiles/dictionaries will
                be generated based on boundary condition of geometries.
            blockMeshDict: Optional input for blockMeshDict. If blockMeshDict is
                not provided, it will be calculated from geometries in XY
                direction and boundary condition for faces will be set to
                BoundingBoxBoundaryCondition. Use BlockMeshDict to create the
                blockMeshDict if your case is not aligned to XY direction or you
                need to assign different boundary condition to geometries.
            meshing_parameters: Optional input for MeshingParameters.
            make2d_parameters: Optional input for make2d_parameters to make a 2d
                case.
        """
        geometries = cls._check_input_geometries(geometries)

        # update meshing_parameters
        if not meshing_parameters:
            meshing_parameters = MeshingParameters()

        # create foam files
        if not blockMeshDict:
            min_pt, max_pt = calculate_min_max_from_bf_geometries(geometries)
            blockMeshDict = BlockMeshDict.from_min_max(
                min_pt, max_pt, convertToMeters)

        if make2d_parameters:
            # create the 2D blockMeshDict
            blockMeshDict.make2d(
                make2d_parameters.origin, make2d_parameters.normal,
                make2d_parameters.width)

        blockMeshDict.update_meshing_parameters(meshing_parameters)

        # set the locationInMesh for snappyHexMeshDict
        if make2d_parameters:
            meshing_parameters.locationInMesh = make2d_parameters.origin
        if not meshing_parameters.locationInMesh:
            meshing_parameters.locationInMesh = blockMeshDict.center

        # rename name for snappyHexMeshDict and stl file if starts with a digit
        normname = '_{}'.format(name) if name[0].isdigit() else name
        snappyHexMeshDict = SnappyHexMeshDict.from_bf_geometries(
            normname, geometries, meshing_parameters,
            convertToMeters=blockMeshDict.convertToMeters)

        # constant folder
        if float(Version.of_ver) < 3:
            turbulenceProperties = RASProperties()
        else:
            turbulenceProperties = TurbulenceProperties()
        transportProperties = TransportProperties()
        g = G()

        # 0 floder
        try:
            _geometries = geometries + blockMeshDict.geometry
        except TypeError:
            _geometries = tuple(geometries) + blockMeshDict.geometry

        u = U.from_bf_geometries(_geometries)
        p = P.from_bf_geometries(_geometries)
        k = K.from_bf_geometries(_geometries)
        epsilon = Epsilon.from_bf_geometries(_geometries)
        nut = Nut.from_bf_geometries(_geometries)
        t = T.from_bf_geometries(_geometries)
        alphat = Alphat.from_bf_geometries(_geometries)
        p_rgh = P_rgh.from_bf_geometries(_geometries)

        # system folder
        fvSchemes = FvSchemes()
        fvSolution = FvSolution()
        controlDict = ControlDict()
        probes = Probes()

        foam_files = (blockMeshDict, snappyHexMeshDict, turbulenceProperties,
                      transportProperties, g, u, p, k, epsilon, nut, t, alphat,
                      p_rgh, fvSchemes, fvSolution, controlDict, probes)

        # create case
        _cls = cls(name, foam_files, geometries)
        _cls.__originalName = normname
        return _cls

    @classmethod
    def from_wind_tunnel(cls, wind_tunnel, make2d_parameters=None):
        """Create case from wind tunnel."""
        _case = cls.from_bf_geometries(
            wind_tunnel.name, wind_tunnel.test_geomtries, wind_tunnel.blockMeshDict,
            wind_tunnel.meshing_parameters, make2d_parameters)

        initialConditions = InitialConditions(
            Uref=wind_tunnel.flow_speed, Zref=wind_tunnel.Zref, z0=wind_tunnel.z0)

        abl_conditions = ABLConditions.from_wind_tunnel(wind_tunnel)

        # add initialConditions and ABLConditions to _case
        _case.add_foam_files((initialConditions, abl_conditions))

        # include condition files in 0 folder files
        _case.U.update_values({'#include': '"initialConditions"',
                               'internalField': 'uniform $flowVelocity'},
                              mute=True)
        _case.p.update_values({'#include': '"initialConditions"',
                               'internalField': 'uniform $pressure'},
                              mute=True)
        _case.k.update_values({'#include': '"initialConditions"',
                               'internalField': 'uniform $turbulentKE'},
                              mute=True)
        _case.epsilon.update_values({'#include': '"initialConditions"',
                                     'internalField': 'uniform $turbulentEpsilon'},
                                    mute=True)

        if wind_tunnel.refinementRegions:
            for region in wind_tunnel.refinementRegions:
                _case.add_refinementRegion(region)

        return _case

    @property
    def isCase(self):
        """return True."""
        return True

    @property
    def project_name(self):
        """Project name."""
        return self.__project_name

    @project_name.setter
    def project_name(self, name):
        assert re.match("^[a-zA-Z0-9_]*$", name), \
            'Invalid project name: "{}".\n' \
            'Do not use whitespace or special charecters.'.format(name)
        self.__project_name = name

    @property
    def geometries(self):
        """Butterfly geometries."""
        if hasattr(self, 'blockMeshDict'):
            try:
                return self.__geometries + self.blockMeshDict.geometry
            except TypeError:
                return tuple(self.__geometries) + self.blockMeshDict.geometry

        return self.__geometries

    @property
    def working_dir(self):
        """Change default working directory.

        Do not change the working dir if you are using OpenFOAM for Windows
        to run the analysis.
        """
        return self.__workingDir

    @working_dir.setter
    def working_dir(self, p):
        self.__workingDir = os.path.normpath(p)

    @property
    def project_dir(self):
        """Get project directory."""
        return os.path.join(self.working_dir, self.project_name)

    @property
    def zero_folder(self):
        """Folder 0 fullpath."""
        return os.path.join(self.project_dir, '0')

    @property
    def constant_folder(self):
        """constant folder fullpath."""
        return os.path.join(self.project_dir, 'constant')

    @property
    def system_folder(self):
        """system folder fullpath."""
        return os.path.join(self.project_dir, 'system')

    @property
    def log_folder(self):
        """log folder fullpath."""
        return os.path.join(self.project_dir, 'log')

    @property
    def polyMesh_folder(self):
        """polyMesh folder fullpath."""
        return os.path.join(self.project_dir, 'constant\\polyMesh')

    @property
    def triSurface_folder(self):
        """triSurface folder fullpath."""
        return os.path.join(self.project_dir, 'constant\\triSurface')

    @property
    def postProcessing_folder(self):
        """postProcessing folder fullpath."""
        return os.path.join(self.project_dir, 'postProcessing')

    @property
    def probes_folder(self):
        """Fullpath to probes folder."""
        return os.path.join(self.postProcessing_folder, 'probes')

    @property
    def foam_files(self):
        """Get all the foam_files."""
        return tuple(f for f in self.__foamfiles)

    @property
    def refinementRegions(self):
        """Get refinement regions."""
        return self.__refinementRegions

    @property
    def is_polyMesh_snappyHexMesh(self):
        """Check if the mesh in polyMesh folder is snappyHexMesh."""
        return len(os.listdir(self.polyMesh_folder)) > 5

    @property
    def probes(self):
        """Get and set Probes."""
        return self.__probes

    @probes.setter
    def probes(self, inp):
        if not inp:
            return

        assert hasattr(inp, 'probeLocations'), \
            "Expected Probes not {}".format(type(inp))

        self.__probes = inp
        if self.probes.probes_count > 0:
            # include probes in controlDict
            self.controlDict.include = self.probes.filename

    def get_foam_file_by_name(self, name):
        """Get a foamfile by name."""
        return self.__get_foam_file_by_name(name, self.foam_files)

    def get_snappyHexMesh_folders(self):
        """Return sorted list of numerical folders."""
        _f = sorted([int(name) for name in os.listdir(self.project_dir)
                     if (name.isdigit() and
                         os.path.isdir(os.path.join(self.project_dir,
                                                    name, 'polyMesh'))
                         )])

        return tuple(str(f) for f in _f)

    def get_result_folders(self):
        """Return sorted list of numerical folders."""
        _f = sorted([int(name) for name in os.listdir(self.project_dir)
                     if (name != '0' and name.isdigit() and
                         os.path.isdir(os.path.join(self.project_dir, name)) and
                         not os.path.isdir(
                         os.path.join(
                             self.project_dir,
                             name,
                             'polyMesh'))
                         )])

        return tuple(str(f) for f in _f)

    def get_foam_files_from_location(self, location=None):
        """Get foam_files in a specific location (0, constant, system)."""
        if not location:
            return tuple(f for f in self.__foamfiles)
        else:
            return tuple(f for f in self.__foamfiles
                         if f.location == '"{}"'.format(location))

    def add_foam_files(self, foamfiles):
        """Add foamfiles to the Case."""
        for ff in foamfiles:
            self.add_foam_file(ff)

    def add_foam_file(self, foamfile):
        """Add a foamfile to the case."""
        if not foamfile:
            return
        assert hasattr(foamfile, 'isFoamFile'), \
            '{} is not a FoamFile'.format(foamfile)
        try:
            setattr(self, foamfile.name, foamfile)
            self.__foamfiles.append(foamfile)
        except AttributeError as e:
            raise ValueError('Failed to add {}.\n\t{}'.format(foamfile, e))

    def add_refinementRegions(self, refinementRegions):
        """Add a collections of refinement regions."""
        for refinementRegion in refinementRegions:
            self.add_refinementRegion(refinementRegion)

    def add_refinementRegion(self, refinementRegion):
        """Add a refinement region."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)
        assert hasattr(self, 'snappyHexMeshDict'), \
            'You can\'t add a refinementRegion to a case with no snappyHexMeshDict.'

        self.snappyHexMeshDict.add_refinementRegion(refinementRegion)

    def copy_snappyHexMesh(self, folder_number=None, overwrite=True):
        """Copy the results of snappyHexMesh to constant/polyMesh."""
        # pick the last numerical folder
        if folder_number:
            _s = os.path.join(self.project_dir, str(folder_number), 'polyMesh')
            assert os.path.isdir(_s), "Can't find {}.".format(_s)
        else:
            _folders = self.get_snappyHexMesh_folders()
            if not _folders:
                return
            _s = os.path.join(self.project_dir, _folders[-1], 'polyMesh')

        # copy files to constant/polyMesh
        if overwrite:
            self.remove_polyMesh_content()

        try:
            copy_tree(_s, self.polyMesh_folder)
        except Exception as e:
            print("Failed to copy snappyHexMesh folder: {}".format(e))

    def rename_snappyHexMesh_folders(self, add=True):
        """Rename snappyHexMesh numerical folders to name.org  and vice versa.

        Args:
            add: Set to True to add .org at the end of the file. Set to False
                to rename them back to the original naming.
        """
        # find list of folders in project and collect the numbers
        if not add:
            _folders = (name for name in os.listdir(self.project_dir)
                        if (name.endswith('.org') and
                            os.path.isdir(os.path.join(self.project_dir, name,
                                                       'polyMesh'))))

            for f in _folders:
                os.rename(os.path.join(self.project_dir, f),
                          os.path.join(self.project_dir, f.replace('.org', '')))
        else:
            _folders = self.get_snappyHexMesh_folders()

            # rename them starting from 1
            for f in _folders:
                try:
                    os.rename(os.path.join(self.project_dir, f),
                              os.path.join(self.project_dir, '%s.org' % f))
                except Exception as e:
                    raise Exception('Failed to rename snappyHexMesh folders: {}'
                                    .format(e))

    def remove_snappyHexMesh_folders(self):
        """Remove snappyHexMesh numerical folders.

        Use this to clean the folder.
        """
        self.rename_snappyHexMesh_folders(add=False)
        _folders = self.get_snappyHexMesh_folders()

        for f in _folders:
            try:
                rmtree(os.path.join(self.project_dir, f))
            except Exception as e:
                print('Failed to remove {}:\n{}'.format(f, e))

    def remove_result_folders(self):
        """Remove results folder."""
        _folders = self.get_result_folders()
        for _f in _folders:
            try:
                rmtree(os.path.join(self.project_dir, _f))
            except Exception as e:
                print('Failed to remove {}:\n{}'.format(_f, e))

    def remove_postProcessing_folder(self):
        """Remove post postProcessing folder."""
        if not os.path.isdir(self.postProcessing_folder):
            return

        try:
            rmtree(self.postProcessing_folder)
        except Exception as e:
            print('Failed to remove postProcessing folder:\n{}'.format(e))

    def remove_polyMesh_content(self):
        """Remove files inside polyMesh folder."""
        for _f in os.listdir(self.polyMesh_folder):
            if _f != 'blockMeshDict':
                _fp = os.path.join(self.polyMesh_folder, _f)
                if os.path.isfile(_fp):
                    os.remove(_fp)
                elif os.path.isdir(_fp):
                    rmtree(_fp)

    def remove_processor_folders(self):
        """Remove processor folders for parallel runs."""

        ff = (os.path.join(self.project_dir, d)
              for d in os.listdir(self.project_dir)
              if d.startswith('processor') and
              os.path.isdir(os.path.join(self.project_dir, d)))

        for f in ff:
            try:
                rmtree(f)
            except Exception as e:
                print('Failed to remove processor folder:\n{}'.format(e))

    def purge(self, remove_polyMesh_content=True,
              remove_snappyHexMesh_folders=True,
              remove_result_folders=False,
              remove_postProcessing_folder=False):
        """Purge case folder."""
        if remove_polyMesh_content:
            self.remove_polyMesh_content()
        if remove_snappyHexMesh_folders:
            self.remove_snappyHexMesh_folders()
        if remove_result_folders:
            self.remove_result_folders()
        if remove_postProcessing_folder:
            self.remove_postProcessing_folder()

    def update_bc_in_zero_folder(self):
        """Update boundary conditions in files in 0 folder.

        Call this method if you have made any changes to boundary condition of
        any of the geometries after initiating the class.
        """
        raise NotImplementedError()

    def save(self, overwrite=False, minimum=True):
        """Save case to folder.

        Args:
            overwrite: If True all the current content will be overwritten
                (default: False).
            minimum: Write minimum necessary files for case. These files will
                be enough for meshing the case but not running any commands.
                Files are ('fvSchemes', 'fvSolution', 'controlDict',
                'blockMeshDict','snappyHexMeshDict'). Rest of the files will be
                created from a Solution.
        """
        # create folder and subfolders if they are not already created
        if overwrite and os.path.exists(self.project_dir):
            rmtree(self.project_dir, ignore_errors=True)

        for f in self.SUBFOLDERS:
            p = os.path.join(self.project_dir, f)
            if not os.path.exists(p):
                try:
                    os.makedirs(p)
                except Exception as e:
                    msg = 'Butterfly failed to create {}\n\t{}'.format(p, e)
                    if str(e).startswith('[Error 183]'):
                        print(msg)
                    else:
                        raise IOError(msg)

        # save foamfiles
        if minimum:
            foam_files = (ff for ff in self.foam_files
                          if ff.name in self.MINFOAMFIles)
        else:
            foam_files = self.foam_files

        for f in foam_files:
            f.save(self.project_dir)

        # find blockMeshDict and convertToMeters so I can scale stl files to meters.
        bmds = (ff for ff in self.foam_files if ff.name == 'blockMeshDict')
        bmd = bmds.next()
        convertToMeters = bmd.convertToMeters

        # write bfgeometries to stl file. __geometries is geometries without
        # blockMesh geometry
        stl_str = (geo.to_stl(convertToMeters) for geo in self.__geometries)
        stl_name = self.__originalName or self.project_name
        with open(os.path.join(self.triSurface_folder,
                               '%s.stl' % stl_name), 'wb') as stlf:
            stlf.writelines(stl_str)

        # write refinementRegions to stl files
        for ref in self.refinementRegions:
            ref.write_to_stl(self.triSurface_folder, convertToMeters)

        # add .foam file
        with open(os.path.join(self.project_dir,
                               self.project_name + '.foam'), 'wb') as ffile:
            ffile.write('')

        print('{} is saved to: {}'.format(self.project_name, self.project_dir))

    def command(self, cmd, args=None, decomposeParDict=None, run=True, wait=True):
        r"""Run an OpenFOAM command for this case.
        This method creates a log and err file under logFolder for each command.
        The output will be logged as {cmd}.log and {cmd}.err.
        Args:
            cmd: OpenFOAM command.
            args: Command arguments.
            decomposeParDict: Optional input for decomposeParDict to run analysis
                in parallel if desired.
            run: Run the command in shell.
            wait: Wait until the command is over.
        returns:
            If run is True returns a namedtuple for
                (success, error, process, logfiles, errorfiles).
                success: as a boolen.
                error: None in case of success otherwise the error message as
                    a string.
                process: Popen process.
                logfiles: List of fullpath to log files.
                errorfiles: List of fullpath to error files.
            else return a namedtuple for
                (cmd, logfiles, errorfiles)
                cmd: command lines.
                logfiles: A tuple for log files.
                errorfiles: A tuple for error files.
        """
        if not run:
            cmdlog = self.runmanager.command(cmd, args, decomposeParDict)
            return cmdlog
        else:
            log = namedtuple('log', 'success error process logfiles errorfiles')

            p, logfiles, errfiles = self.runmanager.run(cmd, args,
                                                        decomposeParDict, wait)

            logfiles = tuple(os.path.normpath(os.path.join(self.project_dir, f))
                             for f in logfiles)

            errfiles = tuple(os.path.normpath(os.path.join(self.project_dir, f))
                             for f in errfiles)

            # check error files and raise and error
            if wait:
                self.runmanager.check_file_contents(logfiles, mute=False)
                hascontent, content = self.runmanager.check_file_contents(errfiles)

                return log(not hascontent, content, p, logfiles, errfiles)
            else:
                # return a namedtuple assuming that the command is running fine.
                return log(True, None, p, logfiles, errfiles)

    def blockMesh(self, args=None, wait=True, overwrite=True,):
        """Run blockMesh.

        Args:
            args: Command arguments.
            wait: Wait until command execution ends.
            overwrite: Overwrite current content of the folder.
        Returns:
            namedtuple(success, error, process, logfiles, errorfiles).
        """
        if overwrite:
            self.remove_polyMesh_content()

        return self.command('blockMesh', args, decomposeParDict=None,
                            wait=wait)

    def surfaceFeatureExtract(self, args=None, wait=True):
        """Run surfaceFeatureExtract command.

        Args:
            args: Command arguments.
            wait: Wait until command execution ends.
        Returns:
            namedtuple(success, error, process, logfiles, errorfiles).
        """
        # create surfaceFeatureExtractDict if it's not created
        return self.command('surfaceFeatureExtract', args, decomposeParDict=None,
                            wait=wait)

    # TODO(Mostapha): Sample for multiple fields.
    # The reason we don't have it now is that I don't have the methods in place
    # for dealing with lists of lists in GRASshopper.
    def sample(self, name, points, field, wait=True):
        """Sample the results for a certain field.

        Args:
            name: A unique name for this sample.
            points: List of points as (x, y, z).
            fields: List of fields (e.g. U, p).
            args: Command arguments.
            wait: Wait until command execution ends.
        Returns:
            namedtuple(probes, values).
        """
        sd = SampleDict.from_points(name, points, (field,))
        sd.save(self.project_dir)

        log = self.command(
            'postProcess', args=('-func', 'sampleDict', '-latestTime'),
            decomposeParDict=None, wait=wait)

        if not log.success:
            raise Exception("Failed to sample the case:\n\t%s"
                            % log.error)

        rf = sorted(int(f) for f in self.get_result_folders())

        assert len(rf) > 0, \
            IOError('Found no results folder. Either you have not run the '
                    'analysis or the run has faild. Check inside "log" folder.')

        fp = tuple(os.path.join(self.postProcessing_folder, 'sampleDict', str(rf[-1]),
                                f)
                   for f in sd.output_filenames)

        if fp:
            res = load_probes_and_values_from_sample_file(fp[0])
            pts, values = zip(*(r for r in res))
            res = namedtuple('Results', 'probes values')
            return res(pts, values)

    def snappyHexMesh(self, args=None, wait=True):
        """Run snappyHexMesh.

        Args:
            args: Command arguments.
            wait: Wait until command execution ends.
        Returns:
            namedtuple(success, error, process, logfiles, errorfiles).
        """
        return self.command('snappyHexMesh', args, self.decomposeParDict,
                            wait=wait)

    def check_mesh(self, args=None, wait=True):
        """Run checkMesh.

        Args:
            args: Command arguments.
            wait: Wait until command execution ends.
        Returns:
            namedtuple(success, error, process, logfiles, errorfiles).
        """
        return self.command('checkMesh', args, self.decomposeParDict,
                            wait=wait)

    def calculate_mesh_orthogonality(self, use_currnt_check_mesh_log=False):
        """Calculate max and average mesh orthogonality.

        If average values is more than 80, try to generate a better mesh.
        You can use this values to set discretization schemes.
        try case.setFvSchemes(average_orthogonality)
        """
        if not use_currnt_check_mesh_log:
            log = self.check_mesh(args=('-latestTime',))
            assert log.success, log.error

        f = os.path.join(self.log_folder, 'checkMesh.log')
        assert os.path.isfile(f), 'Failed to find {}.'.format(f)

        with open(f, 'rb') as inf:
            results = ''.join(inf.readlines())
            maximum, average = results \
                .split('Mesh non-orthogonality Max:')[-1] \
                .split('average:')[:2]

            average = average.split('\n')[0]

        return float(maximum), float(average)

    @staticmethod
    def __get_foam_file_by_name(name, foamfiles):
        """Get a foamfile by name."""
        for f in foamfiles:
            if f.name == name:
                return f

    @staticmethod
    def __create_foamfile_from_file(p, convertToMeters=1):
        """Create a foamfile object from an OpenFOAM foamfile.

        Args:
            p: Fullpath to file.
        Return:
            A Butterfly foam file.
        """
        # Butterfly FoamFiles. This dictionary should be expanded.
        __foamfilescollection = {
            'turbulenceProperties': TurbulenceProperties,
            'RASProperties': RASProperties,
            'transportProperties': TransportProperties, 'g': G,
            'U': U, 'k': K, 'p': P, 'nut': Nut, 'epsilon': Epsilon, 'T': T,
            'alphat': Alphat, 'p_rgh': P_rgh, 'ABLConditions': ABLConditions,
            'initialConditions': InitialConditions,
            'blockMeshDict': BlockMeshDict, 'snappyHexMeshDict': SnappyHexMeshDict,
            'controlDict': ControlDict, 'fvSchemes': FvSchemes,
            'fvSolution': FvSolution, 'probes': Probes,
            'decomposeParDict': DecomposeParDict
        }

        name = os.path.split(p)[-1].split('.')[0]
        if name == 'blockMeshDict':
            try:
                return BlockMeshDict.from_file(p, convertToMeters)
            except Exception as e:
                print('Failed to import {}:\n\t{}'.format(p, e))
        elif name in __foamfilescollection:
            try:
                return __foamfilescollection[name].from_file(p)
            except Exception as e:
                print('Failed to import {}:\n\t{}'.format(p, e))
        else:
            return FoamFile.from_file(p)

    @staticmethod
    def _check_input_geometries(geos):
        for geo in geos:
            assert hasattr(geo, 'isBFMesh'), \
                'Expected butterfly.Mesh not {}'.format(geo)
        return geos

    def load_mesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # This is a abstract property which should be implemented in subclasses
        raise NotImplementedError()

    def load_points(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # This is a abstract property which should be implemented in subclasses
        raise NotImplementedError()

    def load_probe_values(self, field):
        """Return OpenFOAM probes results for a field."""
        if self.probes.probes_count == 0:
            return ()

        if field not in self.probes.fields:
            raise ValueError("Can't find {} in {}.".format(field,
                                                           self.probes.fields))

        return load_probe_values_from_folder(self.probes_folder, field)

    def load_probes(self, field):
        """Return OpenFOAM probes locations for a field."""
        if self.probes.probes_count == 0:
            return ()

        if field not in self.probes.fields:
            raise ValueError("Can't find {} in {}.".format(field,
                                                           self.probes.fields))

        return load_probes_from_postProcessing_file(self.probes_folder, field)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM CASE."""
        return "OpenFOAM CASE: %s" % self.project_name
