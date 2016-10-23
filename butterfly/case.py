"""Butterfly OpenFOAM Case."""
import os

from shutil import rmtree
from distutils.dir_util import copy_tree
from collections import namedtuple
from copy import deepcopy

from .version import Version
from .helper import mkdir, wfile, runbatchfile, readLastLine, \
    loadSkippedProbes, checkFiles, loadCaseFiles
from .geometry import bfGeometryFromStlFile
from .refinementRegion import refinementRegionsFromStlFile
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

from runmanager import RunManager


class Case(object):
    """OpenFOAM Case.

    Attributes:
        name: Case name as a string with no whitespace.
        foamfiles: Collection of FoamFile objects (dictionaries) for this case.
        geometries: Collection of geometry-like objects. Geometries should have
            a name and toStlString method. The information related to boundary
            condition should already be included in related foamfiles. If you
            want to initiate the class form a folder or a number of BFGeometries
            use fromFolder, and fromBFGeometries classmethods.
    """

    __subfolders = ('0', 'constant', 'constant\\polyMesh',
                    'constant\\triSurface', 'system', 'bash', 'bash\\log')

    def __init__(self, name, foamfiles, geometries):
        """Init case."""
        self.__version = float(Version.OFVer)
        self.projectName = name

        # optional input for changing working directory
        # should not be used on OpenFOAM on Windows
        self.workingDir = os.path.join(os.path.expanduser('~'), 'butterfly')
        self.__foamfiles = foamfiles

        # set foamfiles dynamically. This is flexible but makes documentation
        # tricky. also autocomplete won't work for this cases.
        for ff in foamfiles:
            if not ff:
                continue
            assert hasattr(ff, 'isFoamFile'), '{} is not a FoamFile'.format(ff)
            setattr(self, ff.name, ff)

        # set butterfly geometries
        self.geometries = self.__checkInputGeometries(geometries)

        # place holder for refinment regions
        # use .addRefinementRegions to add regions to case
        self.__refinementRegions = []

    # TODO: Parse boundary conditions for each geometry
    @classmethod
    def fromFolder(cls, path, name=None):
        """Create a Butterfly case from a case folder.

        Args:
            path: Full path to case folder.
            name: An optional new name for this case.
        """
        # collect foam files
        if not name:
            name = os.path.split(path)[-1]

        _files = loadCaseFiles(path, True)

        # convert files to butterfly objects
        ff = tuple(cls.__createFoamfileFromFile(p)
                   for f in (_files.zero, _files.constant, _files.system)
                   for p in f)

        # add stl objects

        # find snappyHexMeshDict
        sHMD = cls.__getFoamFileByName('snappyHexMeshDict', ff)

        bfGeometries = tuple(geo for f in _files.stl
                             for geo in bfGeometryFromStlFile(f)
                             if os.path.split(f)[-1][:-4]
                             in sHMD.stlFileNames)

        _case = cls(name, ff, bfGeometries)
        refinementRegions = tuple(
            ref for f in _files.stl
            if os.path.split(f)[-1][:-4] in sHMD.refinementRegionNames
            for ref in refinementRegionsFromStlFile(
                f, sHMD.refinementRegionMode(os.path.split(f)[-1][:-4]))
            )

        _case.addRefinementRegions(refinementRegions)
        return _case

    @property
    def geometries(self):
        """Butterfly geometries."""
        return self.__geometries

    @property
    def workingDir(self):
        """Change default working directory.

        Do not change the working dir if you are using OpenFOAM for Windows
        to run the analysis.
        """
        return self.__workingDir

    @workingDir.setter
    def workingDir(self, p):
        self.__workingDir = os.path.normpath(p)

    @property
    def projectDir(self):
        """Get project directory."""
        return os.path.join(self.workingDir, self.projectName)

    @property
    def zeroFolder(self):
        """Folder 0 fullpath."""
        return os.path.join(self.projectDir, '0')

    @property
    def constantFolder(self):
        """constant folder fullpath."""
        return os.path.join(self.projectDir, 'constant')

    @property
    def systemFolder(self):
        """system folder fullpath."""
        return os.path.join(self.projectDir, 'system')

    @property
    def bashFolder(self):
        """bash folder fullpath."""
        return os.path.join(self.projectDir, 'bash')

    @property
    def logFolder(self):
        """bash folder fullpath."""
        return os.path.join(self.projectDir, 'bash\\log')

    @property
    def polyMeshFolder(self):
        """polyMesh folder fullpath."""
        return os.path.join(self.projectDir, 'constant\\polyMesh')

    @property
    def triSurfaceFolder(self):
        """triSurface folder fullpath."""
        return os.path.join(self.projectDir, 'constant\\triSurface')

    @property
    def foamFiles(self):
        """Get all the foamFiles."""
        return tuple(f for f in self.__foamfiles)

    @property
    def refinementRegions(self):
        """Get refinement regions."""
        return self.__refinementRegions

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
        if self.probes.probesCount > 0:
            # include probes in controlDict
            self.controlDict.include = self.probes.filename

    def getFoamFileByName(self, name):
        """Get a foamfile by name."""
        return self.__getFoamFileByName(name, self.foamFiles)

    def foamFilesByLocation(self, location=None):
        """Get foamFiles in a specific location (0, constant, system)."""
        if not location:
            return tuple(f for f in self.__foamfiles)
        else:
            return tuple(f for f in self.__foamfiles
                         if f.location == '"{}"'.format(location))

    def addRefinementRegions(self, refinementRegions):
        """Add a collections of refinement regions."""
        for refinementRegion in refinementRegions:
            self.addRefinementRegion(refinementRegion)

    def addRefinementRegion(self, refinementRegion):
        """Add a refinement region."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)
        assert hasattr(self, 'snappyHexMeshDict'), \
            'You can\'t add a refinementRegion to a case with no snappyHexMeshDict.'

        self.snappyHexMeshDict.addRefinementRegion(refinementRegion)

    def updateBCInZeroFolder(self):
        """Update boundary conditions in files in 0 folder.

        Call this method if you have made any changes to boundary condition of
        any of the geometries after initiating the class.
        """
        pass

    def save(self, overwrite=False):
        """Save case to folder.

        Args:
            overwrite: If True all the current content will be overwritten
                (default: False).
        """
        # create folder and subfolders if they are not already created
        if overwrite and os.path.exists(self.projectDir):
            rmtree(self.projectDir, ignore_errors=True)

        for f in self.__subfolders:
            p = os.path.join(self.projectDir, f)
            if not os.path.exists(p):
                try:
                    os.makedirs(p)
                except Exception as e:
                    raise IOError(
                        'Butterfly failed to create {}\n{}'.format(p, e)
                    )

        # save foamfiles
        for f in self.foamFiles:
            f.save(self.projectDir)

        # write bfgeometries to stl file
        stlStr = (geo.toSTL() for geo in self.geometries)
        with open(os.path.join(self.triSurfaceFolder,
                               '%s.stl' % self.projectName), 'wb') as stlf:
            stlf.writelines(stlStr)

        # write refinementRegions to stl files
        for ref in self.refinementRegions:
            ref.writeToStl(self.triSurfaceFolder)

        print '{} is saved to:\n{}'.format(self.projectName, self.projectDir)

    @staticmethod
    def __getFoamFileByName(name, foamfiles):
        """Get a foamfile by name."""
        for f in foamfiles:
            if f.name == name:
                return f

    @staticmethod
    def __createFoamfileFromFile(p):
        """
        Create a foamfile object from an OpenFOAM foamfile.

        Args:
            p: Fullpath to file.
        """
        __foamfilescollection = {
            'turbulenceProperties': TurbulenceProperties,
            'RASProperties': RASProperties,
            'transportProperties': TransportProperties, 'g': G,
            'U': U, 'k': K, 'p': P, 'nut': Nut, 'epsilon': Epsilon, 'T': T,
            'alphat': Alphat, 'p_rgh': P_rgh, 'ABLConditions': ABLConditions,
            'initialConditions': InitialConditions,
            'blockMeshDict': BlockMeshDict, 'snappyHexMeshDict': SnappyHexMeshDict,
            'controlDict': ControlDict, 'fvSchemes': FvSchemes,
            'fvSolution': FvSolution, 'probes': Probes
        }

        name = os.path.split(p)[-1]

        if name in __foamfilescollection:
            try:
                return __foamfilescollection[name].fromFile(p)
            except Exception as e:
                print 'Failed to import {}:\n\t{}'.format(p, e)
        else:
            return FoamFile.fromFile(p)

    @staticmethod
    def __checkInputGeometries(geos):
        for geo in geos:
            assert hasattr(geo, 'isBFMesh'), \
                'Expected butterfly.Mesh not {}'.format(geo)
        return geos
